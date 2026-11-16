from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app import db
from app.config import get_settings
from app.core import avisos as av
from app.core import escuela as esc
from app.core.estado import alertas as calcular_alertas
from app.core.pronostico import HORAS_ESCUELA, pronostico_actual

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("")
def listar():
    """Alertas activas: protección baja, aire alto dentro, sensor desconectado y pronóstico."""
    cfg = get_settings()
    with db.conexion() as conn:
        return calcular_alertas(conn, cfg, pronostico_actual(conn, cfg))


@router.get("/hoy")
def hoy():
    """Semáforo del día para el tablero, la vista del maestro y el bot de familias."""
    cfg = get_settings()
    with db.conexion() as conn:
        p = pronostico_actual(conn, cfg)
        activas = calcular_alertas(conn, cfg, p)
        ahora = db.ahora()
        ultima = None
        simulado = False
        desactualizado = True
        if p is not None:
            metricas = p.get("metricas_modelo") or {}
            simulado = bool(p.get("simulado") or metricas.get("sintetico"))
            desactualizado = bool(p.get("desactualizado")) or p["fecha_base"] != ahora.date().isoformat()
            if p["fuente"] == "sensor":
                # La misma ventana que usa _sensor_fuera_hoy: el origen corresponde
                # a los datos consumidos, no a sensores ajenos ni a lecturas de ayer.
                inicio = ahora.replace(hour=min(HORAS_ESCUELA), minute=0, second=0)
                fin = ahora.replace(hour=max(HORAS_ESCUELA), minute=59, second=59)
                fila = conn.execute(
                    "SELECT MAX(ts) AS ultima, MAX(simulada) AS simulada FROM lecturas "
                    "WHERE ubicacion='fuera' AND ts BETWEEN ? AND ?",
                    (inicio.isoformat(), fin.isoformat()),
                ).fetchone()
                ultima = fila["ultima"]
                simulado = simulado or bool(fila["simulada"])
                edad = (ahora - datetime.fromisoformat(ultima)).total_seconds() if ultima else -1
                desactualizado = desactualizado or edad < 0 or edad > cfg.minutos_sin_datos * 60
    procedencia = {
        "fecha_base": p["fecha_base"] if p else None,
        "ultima_lectura": ultima,
        "simulado": simulado,
        "desactualizado": desactualizado,
    }
    if p is None:
        return {"nivel": None, "recomendacion": "Sin datos de calidad del aire todavía.",
                "alertas": activas, **procedencia}
    hoy_, manana = p["dias"]
    return {
        "nivel": hoy_["semaforo"],            # verde | amarillo | rojo (compatible con la versión anterior)
        "pm": hoy_["pm"],
        "categoria": hoy_["nivel"],           # good | ok | bad | vbad | ext (clases CSS del frontend)
        "nombre": hoy_["nombre"],
        "recomendacion": hoy_["consejo"],
        "manana": manana,
        "fuente": p["fuente"],
        "alertas": activas,
        **procedencia,
    }


# ----------------------------------------------------------------------------- avisos a familias
# Contrato del bot de Carlos (bot/bot.py): revisa /aviso/pendientes cada 30 s, reparte por grupo
# y marca /aviso/{id}/enviado. Reemplaza el POST /alertas/aviso en memoria del PR #31.

class AvisoIn(BaseModel):
    escuela_id: str = Field(default="", max_length=40, examples=["miravalle"])
    texto: str = Field(min_length=1, max_length=600)
    grupo: str | None = Field(default=None, max_length=8, examples=["3A"],
                              description="Opcional; sin él, el aviso va a toda la escuela")


class EnviadoIn(BaseModel):
    familias: int = Field(ge=0, le=10000)


class EnviarIn(BaseModel):
    """Lo que manda el botón "Enviar aviso" del tablero (AvisoFamilias.jsx)."""
    mensaje: str | None = Field(default=None, max_length=600)
    escuela_id: str | None = Field(default=None, max_length=40)
    grupo: str | None = Field(default=None, max_length=8)


class ProgramacionIn(BaseModel):
    hora: str = Field(examples=["07:00"])
    mensaje: str | None = Field(default=None, max_length=600)
    escuela_id: str | None = Field(default=None, max_length=40)


def _escuela(escuela_id: str | None) -> str:
    return (escuela_id or "").strip().lower() or get_settings().escuela_default


@router.post("/aviso", status_code=201)
def crear_aviso(aviso: AvisoIn):
    """El director o la maestra mandan un aviso; queda pendiente hasta que el bot lo reparte."""
    with db.conexion() as conn:
        return av.crear_aviso(conn, _escuela(aviso.escuela_id), aviso.texto, aviso.grupo)


@router.get("/aviso")
def historial_avisos(escuela_id: str | None = None, limite: int = Query(default=20, ge=1, le=200)):
    """Últimos avisos (pendientes y enviados), el más reciente primero."""
    with db.conexion() as conn:
        return av.historial(conn, _escuela(escuela_id), limite)


@router.get("/aviso/pendientes")
def avisos_pendientes(escuela_id: str | None = None):
    with db.conexion() as conn:
        return av.pendientes(conn, _escuela(escuela_id))


@router.post("/aviso/{aviso_id}/enviado")
def aviso_enviado(aviso_id: int, cuerpo: EnviadoIn):
    with db.conexion() as conn:
        a = av.marcar_enviado(conn, aviso_id, cuerpo.familias)
    if a is None:
        raise HTTPException(status_code=404, detail=f"No existe el aviso {aviso_id}")
    return a


@router.post("/enviar", status_code=201)
def enviar(cuerpo: EnviarIn | None = None):
    """Atajo del tablero: crea el aviso para toda la escuela. Sin mensaje, usa el texto sugerido."""
    cuerpo = cuerpo or EnviarIn()
    cfg = get_settings()
    escuela = _escuela(cuerpo.escuela_id)
    with db.conexion() as conn:
        texto = (cuerpo.mensaje or "").strip() or esc.mensaje_predeterminado(conn, cfg, escuela)
        return av.crear_aviso(conn, escuela, texto, cuerpo.grupo)


@router.get("/mensaje-familias")
def mensaje_familias(escuela_id: str | None = None):
    """Texto sugerido para el aviso según el pronóstico de mañana."""
    cfg = get_settings()
    with db.conexion() as conn:
        return {"texto": esc.mensaje_predeterminado(conn, cfg, _escuela(escuela_id))}


@router.get("/programacion")
def leer_programacion(escuela_id: str | None = None):
    """Hora del aviso diario (la usan el tablero y el bot)."""
    cfg = get_settings()
    with db.conexion() as conn:
        return av.leer_programacion(conn, _escuela(escuela_id), cfg.hora_aviso)


@router.put("/programacion")
def guardar_programacion(p: ProgramacionIn):
    try:
        with db.conexion() as conn:
            return av.guardar_programacion(conn, _escuela(p.escuela_id), p.hora, p.mensaje)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

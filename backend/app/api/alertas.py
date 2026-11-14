from fastapi import APIRouter

from app import db
from app.config import get_settings
from app.core.estado import alertas as calcular_alertas
from app.core.pronostico import pronostico_actual

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
    if p is None:
        return {"nivel": None, "recomendacion": "Sin datos de calidad del aire todavía.", "alertas": activas}
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
    }

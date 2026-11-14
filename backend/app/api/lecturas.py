from datetime import datetime, timedelta

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app import db
from app.config import get_settings
from app.core.estado import serie_dia
from app.core.nodos import parse_nodo_id

router = APIRouter(prefix="/lecturas", tags=["lecturas"])

PM25_MAX_VALIDO = 1000.0  # el PMS5003 mide hasta 1000 µg/m³; más que eso es error de lectura


class Lectura(BaseModel):
    """Lo que manda el ESP32 (firmware/nodo-aire/src/main.cpp). Solo nodo_id y pm25 son obligatorios."""
    nodo_id: str = Field(examples=["esc-miravalle-salon-3B-dentro"])
    pm25: float = Field(ge=0, le=PM25_MAX_VALIDO)
    pm10: float | None = Field(default=None, ge=0, le=PM25_MAX_VALIDO)
    simulada: bool = False  # True cuando la manda backend/scripts/simular_nodos.py (plan B)


@router.post("", status_code=201)
def recibir(lectura: Lectura, x_nodo_token: str | None = Header(default=None)):
    cfg = get_settings()
    if cfg.nodo_token and x_nodo_token != cfg.nodo_token:
        raise HTTPException(status_code=401, detail="Token de nodo inválido (header X-Nodo-Token)")
    try:
        nodo = parse_nodo_id(lectura.nodo_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    with db.conexion() as conn:
        lid = db.insertar_lectura(conn, nodo_id=lectura.nodo_id, escuela=nodo.escuela, salon_id=nodo.salon_id,
                                  ubicacion=nodo.ubicacion, pm25=lectura.pm25, pm10=lectura.pm10,
                                  simulada=lectura.simulada)
    return {"recibida": lectura.nodo_id, "id": lid, "escuela": nodo.escuela, "salon_id": nodo.salon_id,
            "ubicacion": nodo.ubicacion}


@router.get("")
def listar(salon_id: str | None = None, horas: int = Query(default=24, ge=1, le=24 * 31),
           limite: int = Query(default=500, ge=1, le=5000)):
    """Lecturas crudas más recientes primero."""
    desde = db.ahora() - timedelta(hours=horas)
    with db.conexion() as conn:
        filas = db.lecturas_recientes(conn, salon_id=salon_id, desde=desde, limite=limite)
    return [dict(f) for f in filas]


@router.get("/serie")
def serie(salon_id: str, fecha: str | None = Query(default=None, description="YYYY-MM-DD; por defecto hoy")):
    """Promedio por hora de la jornada (7:00–14:00), fuera y dentro. Misma forma que SERIE del frontend."""
    try:
        dia = datetime.fromisoformat(fecha) if fecha else db.ahora()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="fecha debe ser YYYY-MM-DD") from exc
    with db.conexion() as conn:
        salon = db.obtener_salon(conn, salon_id)
        if salon is None:
            raise HTTPException(status_code=404, detail=f"No existe el salón {salon_id}")
        return serie_dia(conn, salon, dia)


@router.get("/nodos")
def nodos():
    """Última lectura de cada nodo: sirve para revisar en la demo que los dos ESP32 están mandando."""
    with db.conexion() as conn:
        return [dict(f) for f in db.ultima_por_nodo(conn)]

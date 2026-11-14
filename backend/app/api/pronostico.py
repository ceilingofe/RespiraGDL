from fastapi import APIRouter, HTTPException

from app import db
from app.config import get_settings
from app.core.pronostico import pronostico_actual

router = APIRouter(prefix="/pronostico", tags=["pronostico"])


@router.get("")
def pronostico():
    """PM2.5 esperado mañana de 7:00 a 14:00 en la estación de referencia del SIMAJ.

    `dias` tiene la forma de PRONOSTICO en frontend/src/data/demo.js ({dia, pm}) más el semáforo.
    `fuente` dice de dónde salió: modelo, persistencia o sensor.
    """
    cfg = get_settings()
    with db.conexion() as conn:
        p = pronostico_actual(conn, cfg)
    if p is None:
        raise HTTPException(status_code=503, detail="Sin datos para pronosticar: falta la serie del SIMAJ "
                                                    "y no hay lecturas de afuera de hoy.")
    return p

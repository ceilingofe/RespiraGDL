from fastapi import APIRouter, HTTPException

from app import db
from app.config import get_settings
from app.core import escuela as esc

# Archivo propio (escuela.py) para no chocar con escuelas.py del PR #31 (red de escuelas).
router = APIRouter(prefix="/escuelas", tags=["escuelas"])


@router.get("/{escuela_id}")
def escuela(escuela_id: str):
    """Encabezado del tablero: nombre, estación y semáforo de hoy (forma de MOCK_ESCUELA)."""
    cfg = get_settings()
    with db.conexion() as conn:
        e = esc.info_escuela(conn, cfg, escuela_id)
    if e is None:
        raise HTTPException(status_code=404, detail=f"No existe la escuela {escuela_id}")
    return e

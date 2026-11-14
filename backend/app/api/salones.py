from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import db
from app.config import get_settings
from app.core.estado import estado_salon, estados

router = APIRouter(prefix="/salones", tags=["salones"])


class SalonIn(BaseModel):
    """Solo el NÚMERO de alumnos con asma. Nunca nombres ni datos personales."""
    id: str = Field(examples=["3B"], min_length=1, max_length=8)
    escuela: str = Field(examples=["miravalle"])
    grupo: str | None = Field(default=None, examples=["3° B"])
    alumnos_asma: int = Field(ge=0, le=60)
    filtro: bool = True


@router.get("")
def listar(escuela: str | None = None):
    """Todos los salones con fuera, dentro y % de protección (promedio de la última ventana)."""
    cfg = get_settings()
    with db.conexion() as conn:
        return estados(conn, cfg, escuela)


@router.post("", status_code=201)
def guardar(salon: SalonIn):
    with db.conexion() as conn:
        db.upsert_salon(conn, salon.id, salon.escuela.lower(), salon.alumnos_asma, salon.filtro, salon.grupo)
    return {"guardado": salon.id.upper()}


@router.get("/{salon_id}/proteccion")
def proteccion(salon_id: str):
    """% de PM2.5 que no entra = 1 − dentro/fuera (promedio de la última hora)."""
    cfg = get_settings()
    with db.conexion() as conn:
        salon = db.obtener_salon(conn, salon_id)
        if salon is None:
            raise HTTPException(status_code=404, detail=f"No existe el salón {salon_id}")
        e = estado_salon(conn, salon, cfg)
    return {"salon_id": e["id"], "proteccion_pct": e["proteccion"], "estado": e["estado"],
            "fuera": e["fuera"], "dentro": e["dentro"], "fuente_fuera": e["fuente_fuera"],
            "ventana_min": e["ventana_min"]}

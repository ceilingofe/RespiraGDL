from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/lecturas", tags=["lecturas"])

class Lectura(BaseModel):
    nodo_id: str
    pm25: float
    pm10: float | None = None

@router.post("")
def recibir(lectura: Lectura):
    # TODO(Juan): guardar en la base con hora del servidor
    return {"recibida": lectura.nodo_id}

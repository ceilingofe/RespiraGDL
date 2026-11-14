from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.semaforo import nivel, mensaje_familias

router = APIRouter(prefix="/alertas", tags=["alertas"])

@router.get("/hoy")
def hoy():
    # TODO(Juan): usar ml/pronostico para decidir verde / amarillo / rojo por escuela
    return {"nivel": "amarillo", "recomendacion": "Recreo adentro; revisar inhaladores"}


# Pronóstico simulado para el tablero. TODO(Juan): reemplazar con ml/ (persistencia como versión 1).
PRONOSTICO_DEMO = [{"dia": "Hoy", "pm": 62}, {"dia": "Mañana", "pm": 71}, {"dia": "Sábado", "pm": 38}]


@router.get("/pronostico")
def pronostico():
    return [{**p, "nivel": nivel(p["pm"])} for p in PRONOSTICO_DEMO]


@router.get("/mensaje-familias")
def mensaje(zona: str = "Miravalle"):
    return {"texto": mensaje_familias(PRONOSTICO_DEMO[1]["pm"], zona)}


class Aviso(BaseModel):
    escuela_id: str = Field(min_length=1, max_length=40)
    texto: str = Field(min_length=1, max_length=600)


AVISOS: list[dict] = []


@router.post("/aviso", status_code=201)
def aviso(a: Aviso):
    # TODO(Carlos): que el bot de Telegram tome de aquí el aviso y lo mande a las familias suscritas.
    fila = {"id": len(AVISOS) + 1, **a.model_dump()}
    AVISOS.append(fila)
    return fila

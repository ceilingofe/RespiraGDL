from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import db
from app.config import get_settings
from app.core import avisos as av

router = APIRouter(tags=["bot"])


class SuscripcionIn(BaseModel):
    """Solo el chat de Telegram y los grupos. Nunca nombres ni teléfonos."""
    chat_id: str | int
    grupos: list[str] = Field(default_factory=list, max_length=12, examples=[["3A"]])
    escuela_id: str | None = Field(default=None, max_length=40)


class ReporteIn(BaseModel):
    """Respuesta "1" de una familia: solo se cuenta, no se guarda quién respondió."""
    escuela_id: str | None = Field(default=None, max_length=40, alias="escuela")
    grupo: str | None = Field(default=None, max_length=8)

    model_config = {"populate_by_name": True}


def _escuela(escuela_id: str | None) -> str:
    return (escuela_id or "").strip().lower() or get_settings().escuela_default


@router.post("/suscripciones", status_code=201)
def suscribir(s: SuscripcionIn):
    with db.conexion() as conn:
        return av.guardar_suscripcion(conn, str(s.chat_id), _escuela(s.escuela_id), s.grupos)


@router.delete("/suscripciones/{chat_id}")
def desuscribir(chat_id: str):
    with db.conexion() as conn:
        if not av.borrar_suscripcion(conn, chat_id):
            raise HTTPException(status_code=404, detail="Ese chat no estaba suscrito")
    return {"borrada": chat_id}


@router.get("/suscripciones")
def listar_suscripciones(escuela_id: str | None = None, grupo: str | None = None):
    """Chats a los que el bot debe mandar un aviso (filtra por grupo si se indica)."""
    with db.conexion() as conn:
        return av.suscripciones(conn, _escuela(escuela_id), grupo)


@router.post("/reportes-sintomas", status_code=201)
def reportar(r: ReporteIn | None = None):
    r = r or ReporteIn()
    with db.conexion() as conn:
        total = av.reportar_sintomas(conn, _escuela(r.escuela_id), r.grupo)
    return {"total_hoy": total}


@router.get("/reportes-sintomas/hoy")
def reportes_hoy(escuela_id: str | None = None):
    """Cuántas familias respondieron "1" hoy (para el tablero)."""
    with db.conexion() as conn:
        return av.conteo_sintomas(conn, _escuela(escuela_id))

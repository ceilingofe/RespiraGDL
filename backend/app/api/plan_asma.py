"""Plan de asma escolar: protocolo por nivel y registro anónimo de crisis.

Ética: nunca se guarda nombre, CURP ni diagnóstico. Solo grupo, hora y si se avisó a la familia.
Demo: el registro vive en memoria. TODO(Juan): pasarlo a la base de datos de /lecturas.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field

from app.services.semaforo import protocolo, NIVELES, PROTOCOLO

router = APIRouter(prefix="/plan-asma", tags=["plan de asma"])
TZ = ZoneInfo("America/Mexico_City")

PASOS_CRISIS = [
    "Mantén la calma y quédate con el alumno. Siéntalo derecho, un poco inclinado hacia adelante, lejos de humo o polvo.",
    "Ayúdalo a usar su inhalador de rescate como indica su plan firmado por su médico.",
    "Observa si mejora en el tiempo que marca su plan. Si no mejora, repite como indica el plan y avisa a la dirección.",
    "Si le cuesta hablar, tiene los labios o uñas morados, o no mejora: llama al 911.",
    "Avisa a la familia y registra la hora. El registro es anónimo: solo grupo y hora.",
]


class Incidente(BaseModel):
    # extra="forbid": si alguien manda "nombre" u otro campo, se rechaza en vez de guardarlo.
    model_config = ConfigDict(extra="forbid")
    salon_id: str = Field(min_length=1, max_length=8, pattern=r"^[0-9A-Za-z]+$")
    aviso_familia: bool = False
    llamada_911: bool = False


_INCIDENTES: list[dict] = []


@router.get("/protocolo")
def get_protocolo(pm25: float = Query(ge=0, description="PM2.5 en µg/m³")):
    return protocolo(pm25)


@router.get("/niveles")
def niveles():
    return [
        {"id": i, "nombre": n, "color": c, "max": None if m == float("inf") else m, **PROTOCOLO[i]}
        for i, n, c, m in NIVELES
    ]


@router.get("/guia-crisis")
def guia_crisis():
    return {"pasos": PASOS_CRISIS, "aviso": "Borrador. Debe validarlo un médico. No sustituye la atención médica."}


@router.post("/incidentes", status_code=201)
def registrar(incidente: Incidente):
    ahora = datetime.now(TZ)
    fila = {
        "id": len(_INCIDENTES) + 1,
        "fecha": ahora.date().isoformat(),
        "hora": ahora.strftime("%H:%M"),
        **incidente.model_dump(),
    }
    _INCIDENTES.append(fila)
    return fila


@router.get("/incidentes")
def listar(salon_id: str | None = None):
    filas = [f for f in _INCIDENTES if salon_id is None or f["salon_id"] == salon_id]
    return sorted(filas, key=lambda f: f["id"], reverse=True)


@router.get("/indicadores")
def indicadores():
    total = len(_INCIDENTES)
    if total == 0:
        return {"crisis": 0, "con_aviso_familia": 0, "llamadas_911": 0, "por_salon": {}}
    por_salon: dict[str, int] = {}
    for f in _INCIDENTES:
        por_salon[f["salon_id"]] = por_salon.get(f["salon_id"], 0) + 1
    return {
        "crisis": total,
        "con_aviso_familia": sum(f["aviso_familia"] for f in _INCIDENTES),
        "llamadas_911": sum(f["llamada_911"] for f in _INCIDENTES),
        "por_salon": por_salon,
    }


def _reiniciar():  # solo para pruebas
    _INCIDENTES.clear()



"""Red de escuelas piloto para la vista de autoridades. Datos simulados de la demo.

TODO(Juan): calcular pm_hoy y pm_manana con el modelo de ml/ y la estación del SIMAJ de cada escuela.
"""
from fastapi import APIRouter, HTTPException

from app.services.semaforo import nivel, protocolo

router = APIRouter(prefix="/escuelas", tags=["escuelas"])

ESCUELAS = [
    {"id": "miravalle", "nombre": "Primaria Miravalle", "municipio": "Guadalajara", "estacion": "SIMAJ Miravalle",
     "pmHoy": 62, "pmManana": 71, "salones": 6, "conFiltro": 4, "proteccion": 65, "asma": 15,
     "faltas": {"antes": 38, "ahora": 24}, "recreo": 21, "fueraNorma": 23},
    {"id": "las-pintas", "nombre": "Primaria Las Pintas", "municipio": "Tlaquepaque", "estacion": "SIMAJ Las Pintas",
     "pmHoy": 74, "pmManana": 82, "salones": 8, "conFiltro": 3, "proteccion": 58, "asma": 19,
     "faltas": {"antes": 44, "ahora": 35}, "recreo": 17, "fueraNorma": 29},
    {"id": "santa-fe", "nombre": "Primaria Santa Fe", "municipio": "Tlajomulco", "estacion": "SIMAJ Santa Fe",
     "pmHoy": 41, "pmManana": 49, "salones": 6, "conFiltro": 6, "proteccion": 71, "asma": 11,
     "faltas": {"antes": 21, "ahora": 13}, "recreo": 14, "fueraNorma": 15},
]


@router.get("")
def listar():
    return [{**e, "nivelHoy": nivel(e["pmHoy"]), "nivelManana": nivel(e["pmManana"])} for e in ESCUELAS]


@router.get("/{escuela_id}/plan-manana")
def plan_manana(escuela_id: str):
    e = next((x for x in ESCUELAS if x["id"] == escuela_id), None)
    if e is None:
        raise HTTPException(404, "Escuela no encontrada")
    return {"escuela_id": escuela_id, **protocolo(e["pmManana"])}

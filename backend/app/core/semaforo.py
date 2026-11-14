"""Niveles de calidad del aire por PM2.5 y su color de semáforo para la escuela.

Cortes del Índice AIRE y SALUD para PM2.5 de la NOM-172-SEMARNAT-2023 (DOF, enero de 2024),
Tabla 5, columna vigente "a partir de enero de 2026": Buena <=15, Aceptable >15 a 25,
Mala >25 a 79, Muy mala >79 a 130, Extremadamente mala >130 µg/m³. La norma los aplica al
promedio móvil ponderado de 12 h; aquí se aplican al valor que se le pase (simplificación
documentada en docs/metodo-y-datos.md). El frontend (frontend/src/data/demo.js) debe usar
estos mismos cortes.

Semáforo de la escuela:
  verde    -> Buena o Aceptable: recreo normal
  amarillo -> Mala: recreo adentro para niños con asma
  rojo     -> Muy mala o peor: recreo adentro para todos
"""
from __future__ import annotations

import math

# id (igual que las clases CSS del frontend), nombre, máximo µg/m³, semáforo, consejo
NIVELES = [
    ("good", "Buena", 15.0, "verde", "Recreo normal al aire libre."),
    ("ok", "Aceptable", 25.0, "verde", "Recreo normal; vigilar a niños con asma."),
    ("bad", "Mala", 79.0, "amarillo", "Recreo adentro para niños con asma; filtro encendido."),
    ("vbad", "Muy mala", 130.0, "rojo", "Recreo adentro para todos; ventanas cerradas y filtro al máximo."),
    ("ext", "Extremadamente mala", math.inf, "rojo", "Seguir indicaciones de Protección Civil."),
]

ORDEN_SEMAFORO = {"verde": 0, "amarillo": 1, "rojo": 2}


def nivel(pm25: float | None) -> dict | None:
    """Devuelve el nivel para un valor de PM2.5 en µg/m³ (None si no hay dato)."""
    if pm25 is None or (isinstance(pm25, float) and math.isnan(pm25)):
        return None
    for nid, nombre, maximo, semaforo, consejo in NIVELES:
        if pm25 <= maximo:
            return {"id": nid, "nombre": nombre, "semaforo": semaforo, "consejo": consejo}
    raise AssertionError("inalcanzable")


def semaforo(pm25: float | None) -> str | None:
    n = nivel(pm25)
    return n["semaforo"] if n else None

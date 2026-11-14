"""Carga los salones de la demo y, si se pide, lecturas SIMULADAS de hoy.

    cd backend
    python -m scripts.cargar_demo                 # solo salones (lo mínimo para la demo real)
    python -m scripts.cargar_demo --lecturas      # + lecturas simuladas de las últimas 8 horas
    python -m scripts.cargar_demo --borrar-simuladas

Los salones y el número de alumnos con asma son los mismos de frontend/src/data/demo.js.
Las lecturas simuladas quedan marcadas con simulada=1 para poder decir en la demo qué
parte es simulada (regla 5 del kit) y borrarlas antes de medir con los sensores reales.
"""
from __future__ import annotations

import argparse
import math
import random
from datetime import timedelta

from app import db

ESCUELA = "miravalle"
# id, grupo, alumnos con asma (solo el número), tiene filtro
SALONES = [
    ("1A", "1° A", 3, True),
    ("2A", "2° A", 2, True),
    ("3A", "3° A", 4, True),
    ("4B", "4° B", 1, False),
    ("5A", "5° A", 2, True),
    ("6B", "6° B", 3, False),
]


def pm_fuera(hora_decimal: float) -> float:
    """Curva típica de un día con mala calidad del aire: pico a media mañana."""
    return 45 + 22 * math.exp(-((hora_decimal - 10.0) ** 2) / 4.0)


def cargar_salones(conn) -> None:
    for sid, grupo, asma, filtro in SALONES:
        db.upsert_salon(conn, sid, ESCUELA, asma, filtro, grupo)


def cargar_lecturas(conn, cada_min: int = 5, semilla: int = 7) -> int:
    rnd = random.Random(semilla)
    ahora = db.ahora()
    # Las últimas 8 horas hasta ahora: así el tablero tiene datos aunque se ensaye de noche.
    t = (ahora - timedelta(hours=8)).replace(second=0)
    inicio = t
    n = 0
    while t <= ahora:
        h = t.hour + t.minute / 60
        fuera = max(5.0, pm_fuera(h) + rnd.gauss(0, 3))
        db.insertar_lectura(conn, nodo_id=f"esc-{ESCUELA}-fuera", escuela=ESCUELA, salon_id=None,
                            ubicacion="fuera", pm25=round(fuera, 1), ts=t, simulada=True)
        n += 1
        for sid, _g, _a, filtro in SALONES:
            # el filtro tarda ~1 h en "limpiar" el salón después de encenderlo
            eficiencia = (0.68 if filtro else 0.08) * (1 - math.exp(-((t - inicio).seconds / 3600) / 0.5))
            dentro = max(2.0, fuera * (1 - eficiencia) + rnd.gauss(0, 2))
            db.insertar_lectura(conn, nodo_id=f"esc-{ESCUELA}-salon-{sid}-dentro", escuela=ESCUELA,
                                salon_id=sid, ubicacion="dentro", pm25=round(dentro, 1), ts=t, simulada=True)
            n += 1
        t += timedelta(minutes=cada_min)
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lecturas", action="store_true", help="agrega lecturas simuladas de las últimas 8 horas")
    ap.add_argument("--borrar-simuladas", action="store_true", help="borra todas las lecturas simuladas")
    args = ap.parse_args()
    with db.conexion() as conn:
        if args.borrar_simuladas:
            n = conn.execute("DELETE FROM lecturas WHERE simulada = 1").rowcount
            print(f"Borradas {n} lecturas simuladas")
            return
        cargar_salones(conn)
        print(f"Salones cargados: {', '.join(s[0] for s in SALONES)} (escuela {ESCUELA})")
        if args.lecturas:
            print(f"Lecturas SIMULADAS insertadas: {cargar_lecturas(conn)}")


if __name__ == "__main__":
    main()

"""Simula los dos ESP32 mandando lecturas a la API (plan B si no llega el PMS5003).

    cd backend
    python -m scripts.simular_nodos --api http://localhost:8000 --salon 3A --cada 10
    python -m scripts.simular_nodos --csv lecturas_grabadas.csv     # reproduce lecturas reales grabadas

Manda el mismo JSON que firmware/nodo-aire/src/main.cpp más "simulada": true, para que la
API las marque como simuladas. El CSV grabado debe tener columnas nodo_id,pm25[,pm10].
Solo usa la librería estándar.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import time
import urllib.request

from scripts.cargar_demo import ESCUELA, pm_fuera


def enviar(api: str, cuerpo: dict, token: str | None) -> int:
    req = urllib.request.Request(f"{api.rstrip('/')}/lecturas", data=json.dumps(cuerpo).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    if token:
        req.add_header("X-Nodo-Token", token)
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--salon", default="3A")
    ap.add_argument("--cada", type=float, default=10, help="segundos entre lecturas")
    ap.add_argument("--filtro", type=float, default=0.65, help="fracción de PM2.5 que quita el filtro")
    ap.add_argument("--csv", help="reproducir un CSV de lecturas grabadas en lugar de generar")
    ap.add_argument("--token", help="valor de NODO_TOKEN si la API lo pide")
    args = ap.parse_args()

    if args.csv:
        with open(args.csv, newline="", encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        for fila in filas:
            cuerpo = {"nodo_id": fila["nodo_id"], "pm25": float(fila["pm25"]), "simulada": True}
            if fila.get("pm10"):
                cuerpo["pm10"] = float(fila["pm10"])
            print(cuerpo["nodo_id"], cuerpo["pm25"], "->", enviar(args.api, cuerpo, args.token))
            time.sleep(args.cada)
        return

    rnd = random.Random()
    print("Simulando nodos (Ctrl+C para parar). Estas lecturas quedan marcadas como simuladas.")
    while True:
        h = time.localtime().tm_hour + time.localtime().tm_min / 60
        fuera = max(5.0, pm_fuera(h) + rnd.gauss(0, 3))
        dentro = max(2.0, fuera * (1 - args.filtro) + rnd.gauss(0, 2))
        for nodo, pm in ((f"esc-{ESCUELA}-salon-{args.salon}-fuera", fuera),
                         (f"esc-{ESCUELA}-salon-{args.salon}-dentro", dentro)):
            estado = enviar(args.api, {"nodo_id": nodo, "pm25": round(pm, 1), "simulada": True}, args.token)
            print(f"{nodo:40s} PM2.5={pm:5.1f} -> {estado}")
        time.sleep(args.cada)


if __name__ == "__main__":
    main()

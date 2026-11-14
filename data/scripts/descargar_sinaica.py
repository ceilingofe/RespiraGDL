"""Baja datos horarios del SIMAJ vía SINAICA (dataset 39) a data/raw/.

Dataset 39 del kit: Calidad del aire en Jalisco (SIMAJ / SINAICA), SEMADET Jalisco / INECC.
Consulta: aire.jalisco.gob.mx · sinaica.inecc.gob.mx (datos)

Uso (desde la raíz del repo):
    # 1. Encontrar los IDs de Las Pintas, Santa Fe, etc.
    python data/scripts/descargar_sinaica.py --buscar

    # 2. Descargar (un CSV por estación y parámetro en data/raw/)
    python data/scripts/descargar_sinaica.py --estacion Miravalle=106 --estacion Centro=102 \
        --estacion "Las Pintas=<id>" --estacion "Santa Fe=<id>" --desde 2022-01-01 --hasta 2026-11-13

Los crudos NO se suben al repo (.gitignore excluye data/raw/*).
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "backend"))

from app.services import sinaica  # noqa: E402


def _estacion(texto: str) -> tuple[str, int]:
    if "=" not in texto:
        if texto in sinaica.ESTACIONES_CONOCIDAS:
            return texto, sinaica.ESTACIONES_CONOCIDAS[texto]
        raise argparse.ArgumentTypeError(f"Usa Nombre=ID (p. ej. 'Las Pintas=103'); conocidas: "
                                         f"{sinaica.ESTACIONES_CONOCIDAS}")
    nombre, sid = texto.rsplit("=", 1)
    return nombre.strip(), int(sid)


def buscar(ids: range) -> None:
    print("Leyendo el menú de estaciones de", sinaica.URL_PAGINA)
    try:
        estaciones = sinaica.listar_estaciones_pagina()
    except Exception as exc:
        estaciones = {}
        print("  no se pudo leer:", exc)
    gdl = {i: n for i, n in estaciones.items() if any(
        p in n.lower() for p in ("miravalle", "pintas", "santa fe", "centro", "tlaquepaque", "loma dorada",
                                 "oblatos", "atemajac", "vallarta", "águilas", "aguilas", "las águilas"))}
    for i, n in sorted(gdl.items()):
        print(f"  {i:4d}  {n}")
    if not gdl:
        print("  El menú no vino en el HTML. Probando IDs con datos de PM2.5 de la semana pasada...")
        ini = date.today() - timedelta(days=7)
        for i in ids:
            try:
                filas = sinaica.parsear_respuesta(sinaica._post(sinaica.URL_DATOS, {
                    "estacionId": i, "param": "PM2.5", "fechaIni": ini.isoformat(), "rango": 2,
                    "tipoDatos": ""}))
            except Exception as exc:
                print(f"  {i}: error {exc}")
                continue
            if filas:
                print(f"  {i:4d}  tiene {len(filas)} horas de PM2.5 (confirmar el nombre en data.php)")
    print("\nConfirma el nombre de cada ID en https://sinaica.inecc.gob.mx/data.php antes de usarlo.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--buscar", action="store_true", help="lista IDs de estaciones de la ZMG")
    ap.add_argument("--rango-ids", default="95-125", help="IDs a probar con --buscar (por defecto 95-125)")
    ap.add_argument("--estacion", action="append", type=_estacion, help="Nombre=ID; se puede repetir")
    ap.add_argument("--parametro", action="append", help=f"por defecto {', '.join(sinaica.PARAMETROS)}")
    ap.add_argument("--desde", type=date.fromisoformat, default=date(2022, 1, 1))
    ap.add_argument("--hasta", type=date.fromisoformat, default=date.today())
    ap.add_argument("--tipo", choices=sinaica.TIPOS, default="crudos",
                    help="crudos (tiempo real, lo más reciente) o validados (más limpios, con retraso)")
    ap.add_argument("--salida", type=Path, default=RAIZ / "data" / "raw")
    args = ap.parse_args()

    if args.buscar:
        a, b = (int(x) for x in args.rango_ids.split("-"))
        buscar(range(a, b + 1))
        return

    estaciones = args.estacion or list(sinaica.ESTACIONES_CONOCIDAS.items())
    parametros = args.parametro or list(sinaica.PARAMETROS)
    args.salida.mkdir(parents=True, exist_ok=True)

    for nombre, sid in estaciones:
        for param in parametros:
            print(f"{nombre} ({sid}) · {param} · {args.desde} a {args.hasta} · {args.tipo}")
            filas = sinaica.descargar_rango(sid, param, args.desde, args.hasta, args.tipo)
            if not filas:
                print("  sin datos (la estación quizá no mide este parámetro)")
                continue
            archivo = args.salida / f"sinaica_{nombre.replace(' ', '_')}_{param.replace('.', '')}_{args.tipo}.csv"
            with archivo.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["estacion", "estacion_id", "parametro", "fecha", "hora",
                                                  "valor", "valido"])
                w.writeheader()
                for fila in filas:
                    w.writerow({"estacion": nombre, "estacion_id": sid, "parametro": param, **fila})
            print(f"  -> {archivo.relative_to(RAIZ)} ({len(filas)} filas)")


if __name__ == "__main__":
    main()

"""Limpia los CSV de data/raw/ y arma la serie horaria que usan el modelo y la API.

    python data/scripts/procesar_sinaica.py
    -> data/processed/simaj_horario.csv   (fecha_hora, estacion, pm25, pm10, tmp, hr, vv)
    -> data/processed/resumen_datos.csv   (cobertura por estación: para el reporte)

Limpieza (se documenta en docs/metodo-y-datos.md):
  * valores negativos -> vacío
  * PM2.5 > 175 y PM10 > 600 µg/m³ -> vacío (mismos topes que la página de SINAICA)
  * hora 24 -> 0:00 del día siguiente (algunas estaciones reportan 1–24)
  * huecos de hasta 3 horas se interpolan; huecos más largos se dejan vacíos
  * un valor por estación y hora (si hay duplicados, se promedian)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
TOPES = {"PM2.5": 175.0, "PM10": 600.0}
COLUMNAS = {"PM2.5": "pm25", "PM10": "pm10", "TMPI": "tmp", "TMP": "tmp", "HR": "hr", "VV": "vv"}
MAX_HUECO_H = 3


def leer_crudos(carpeta: Path) -> pd.DataFrame:
    archivos = sorted(carpeta.glob("sinaica_*.csv"))
    if not archivos:
        raise SystemExit(f"No hay CSV en {carpeta}. Corre primero data/scripts/descargar_sinaica.py")
    df = pd.concat((pd.read_csv(a, dtype={"fecha": str}) for a in archivos), ignore_index=True)
    print(f"Leídos {len(archivos)} archivos, {len(df):,} filas")
    return df


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df.loc[df["valor"] < 0, "valor"] = pd.NA
    for p, tope in TOPES.items():
        df.loc[(df["parametro"] == p) & (df["valor"] > tope), "valor"] = pd.NA
    df["hora"] = pd.to_numeric(df["hora"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["fecha", "hora"])
    df["fecha_hora"] = pd.to_datetime(df["fecha"]) + pd.to_timedelta(df["hora"].astype(int), unit="h")
    df["variable"] = df["parametro"].map(COLUMNAS)
    df = df.dropna(subset=["variable"])
    ancho = df.pivot_table(index=["estacion", "fecha_hora"], columns="variable", values="valor",
                           aggfunc="mean").reset_index()
    ancho.columns.name = None
    partes = []
    for est, g in ancho.groupby("estacion"):
        g = g.set_index("fecha_hora").sort_index()
        idx = pd.date_range(g.index.min(), g.index.max(), freq="h")
        g = g.reindex(idx)
        g.index.name = "fecha_hora"
        g["estacion"] = est
        num = [c for c in ("pm25", "pm10", "tmp", "hr", "vv") if c in g.columns]
        g[num] = g[num].interpolate(limit=MAX_HUECO_H, limit_area="inside")
        partes.append(g.reset_index())
    salida = pd.concat(partes, ignore_index=True)
    columnas = ["fecha_hora", "estacion"] + [c for c in ("pm25", "pm10", "tmp", "hr", "vv") if c in salida]
    return salida[columnas]


def resumen(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for est, g in df.groupby("estacion"):
        filas.append({
            "estacion": est,
            "desde": g["fecha_hora"].min().date(),
            "hasta": g["fecha_hora"].max().date(),
            "horas": len(g),
            "pct_pm25_con_dato": round(100 * g["pm25"].notna().mean(), 1) if "pm25" in g else 0,
            "pm25_promedio": round(g["pm25"].mean(), 1) if "pm25" in g else None,
            # 25 µg/m³ = límite de PM2.5 a 24 h de la NOM-025-SSA1-2021 vigente desde enero de 2026
            "dias_promedio24h_mayor_25": int((g.set_index("fecha_hora")["pm25"].resample("D").mean() > 25).sum())
            if "pm25" in g else None,
        })
    return pd.DataFrame(filas)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrada", type=Path, default=RAIZ / "data" / "raw")
    ap.add_argument("--salida", type=Path, default=RAIZ / "data" / "processed")
    args = ap.parse_args()
    df = limpiar(leer_crudos(args.entrada))
    args.salida.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.salida / "simaj_horario.csv", index=False)
    r = resumen(df)
    r.to_csv(args.salida / "resumen_datos.csv", index=False)
    print(r.to_string(index=False))
    print(f"\n-> {args.salida / 'simaj_horario.csv'} ({len(df):,} filas)")


if __name__ == "__main__":
    main()

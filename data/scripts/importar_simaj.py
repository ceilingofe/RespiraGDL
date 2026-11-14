"""Convierte la base histórica del SIMAJ (BD_<año>.xlsx) al formato crudo del pipeline.

Fuente: Base histórica de calidad del aire, SIMAJ, SEMADET Jalisco, aire.jalisco.gob.mx
(portal airejalisco.digital, sección Datos → "Base histórica completa"; cada año se baja de
https://airejalisco.digital/assets/files/historical/BD_<año>.xlsx a data/raw/simaj/).

    python data/scripts/importar_simaj.py
    -> data/raw/sinaica_<Estacion>_<PARAM>_simaj.csv
       (columnas estacion,estacion_id,parametro,fecha,hora,valor,valido)

Formato de origen (hoja "Data" de cada libro):
  * STATION: clave de la estación (MIR, CEN, PIN, SFE, ...)
  * DATE: fecha y hora local; HOUR: 0-23
  * Unidades (hoja "Param"): PM10 y PM2.5 en µg/m³, ET/IT en °C, RH en %, WS en m/s
  * Faltantes: celda vacía; a veces banderas de texto (IF, IO, IR, ND, VE, SD) -> vacío
  * Se usa ET (temperatura externa) como TMP del pipeline

Con eso, data/scripts/procesar_sinaica.py y ml/entrenar.py corren SIN cambios.
Los IDs de estación son los de SINAICA, para que todo el pipeline use los mismos.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]

# clave del SIMAJ -> (nombre del pipeline, id de SINAICA)
ESTACIONES = {
    "MIR": ("Miravalle", 106),
    "CEN": ("Centro", 102),
    "PIN": ("Las Pintas", 104),
    "SFE": ("Santa Fe", 108),
}

# columna del SIMAJ -> nombre de parámetro que entiende procesar_sinaica.py
PARAMETROS = {"PM2.5": "PM2.5", "PM10": "PM10", "ET": "TMP", "RH": "HR", "WS": "VV"}


def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    """Hoja "Data" de un BD_<año>.xlsx -> formato largo del pipeline.

    Descarta estaciones que no usamos, banderas de texto y celdas vacías.
    """
    df = df.rename(columns=lambda c: str(c).strip())
    df = df[df["STATION"].isin(ESTACIONES)]
    fecha = pd.to_datetime(df["DATE"]).dt.strftime("%Y-%m-%d")
    hora = pd.to_numeric(df["HOUR"], errors="coerce").astype("Int64")
    partes = []
    for origen, destino in PARAMETROS.items():
        if origen not in df.columns:
            continue
        valor = pd.to_numeric(df[origen], errors="coerce")  # banderas IF/IO/IR/ND/VE/SD -> NaN
        parte = pd.DataFrame({
            "estacion": df["STATION"].map(lambda c: ESTACIONES[c][0]),
            "estacion_id": df["STATION"].map(lambda c: ESTACIONES[c][1]),
            "parametro": destino,
            "fecha": fecha,
            "hora": hora,
            "valor": valor,
            "valido": 1,
        })
        partes.append(parte.dropna(subset=["hora", "valor"]))
    if not partes:
        return pd.DataFrame(columns=["estacion", "estacion_id", "parametro", "fecha", "hora", "valor", "valido"])
    return pd.concat(partes, ignore_index=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrada", type=Path, default=RAIZ / "data" / "raw" / "simaj")
    ap.add_argument("--salida", type=Path, default=RAIZ / "data" / "raw")
    args = ap.parse_args()

    archivos = sorted(args.entrada.glob("BD_*.xlsx"))
    if not archivos:
        raise SystemExit(f"No hay BD_<año>.xlsx en {args.entrada}. Descárgalos de airejalisco.digital.")

    todo = []
    for archivo in archivos:
        df = pd.read_excel(archivo, sheet_name="Data")
        normal = normalizar(df)
        print(f"{archivo.name}: {len(df):,} filas crudas -> {len(normal):,} valores útiles")
        todo.append(normal)
    junto = pd.concat(todo, ignore_index=True)

    args.salida.mkdir(parents=True, exist_ok=True)
    for (estacion, parametro), grupo in junto.groupby(["estacion", "parametro"]):
        archivo = args.salida / f"sinaica_{estacion.replace(' ', '_')}_{parametro.replace('.', '')}_simaj.csv"
        grupo.to_csv(archivo, index=False)
        print(f"  -> {archivo.relative_to(RAIZ)} ({len(grupo):,} filas)")


if __name__ == "__main__":
    main()

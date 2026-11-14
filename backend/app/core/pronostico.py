"""Pronóstico de PM2.5 para mañana en horario escolar (7:00–14:00).

Lo comparten el entrenamiento (ml/entrenar.py) y la API (/pronostico), así las variables
son exactamente las mismas en los dos lados.

Entrada: serie HORARIA de una estación del SIMAJ con columnas
    fecha_hora, estacion, pm25 [, pm10, tmp, hr, vv]
(data/scripts/procesar_sinaica.py la genera en data/processed/simaj_horario.csv).

Objetivo: y(d) = promedio de PM2.5 de 7:00 a 14:00 del día d+1.
Línea base: persistencia, y_hat(d) = promedio escolar del día d ("mañana = hoy").
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from app.core.semaforo import nivel

HORAS_ESCUELA = range(7, 15)        # 7:00 a 14:00 inclusive
MIN_HORAS_VALIDAS = 5               # de 8 horas escolares, al menos 5 con dato
METEO = ("tmp", "hr", "vv")

FEATURES = [
    "pm_escolar", "pm_dia", "pm_tarde", "pm_max", "pm_escolar_ayer", "pm_media_3d",
    "tmp", "hr", "vv", "dow_manana", "mes_sin", "mes_cos",
]


def _pd():
    import pandas as pd  # import tardío: la API arranca aunque no se use el pronóstico

    return pd


def cargar_serie(path: Path | str, estacion: str):
    pd = _pd()
    df = pd.read_csv(path, parse_dates=["fecha_hora"])
    if "estacion" in df.columns:
        sel = df[df["estacion"].str.casefold() == estacion.casefold()]
        if sel.empty:
            disponibles = ", ".join(sorted(df["estacion"].unique()))
            raise ValueError(f"No hay datos de la estación '{estacion}'. Disponibles: {disponibles}")
        df = sel
    return df.sort_values("fecha_hora").reset_index(drop=True)


def features_diarias(df_horario):
    """Una fila por día d con las variables conocidas al cierre de d y el objetivo y = escolar(d+1)."""
    import numpy as np

    pd = _pd()
    h = df_horario.copy()
    h["fecha"] = h["fecha_hora"].dt.normalize()
    h["hora"] = h["fecha_hora"].dt.hour

    esc = h[h["hora"].isin(HORAS_ESCUELA)].groupby("fecha")["pm25"]
    pm_escolar = esc.mean().where(esc.count() >= MIN_HORAS_VALIDAS)

    g = h.groupby("fecha")
    dia = pd.DataFrame({
        "pm_escolar": pm_escolar,
        "pm_dia": g["pm25"].mean().where(g["pm25"].count() >= 16),
        "pm_tarde": h[h["hora"].between(15, 20)].groupby("fecha")["pm25"].mean(),
        "pm_max": g["pm25"].max(),
    })
    for m in METEO:
        dia[m] = g[m].mean() if m in h.columns else np.nan

    # Días calendario completos para que los rezagos no salten huecos
    idx = pd.date_range(dia.index.min(), dia.index.max(), freq="D")
    dia = dia.reindex(idx)
    dia.index.name = "fecha"

    dia["pm_escolar_ayer"] = dia["pm_escolar"].shift(1)
    dia["pm_media_3d"] = dia["pm_dia"].rolling(3, min_periods=2).mean()
    manana = dia.index + pd.Timedelta(days=1)
    dia["dow_manana"] = manana.dayofweek
    dia["mes_sin"] = np.sin(2 * np.pi * manana.month / 12)
    dia["mes_cos"] = np.cos(2 * np.pi * manana.month / 12)
    dia["y"] = dia["pm_escolar"].shift(-1)
    return dia


def predecir_desde_serie(df_horario, bundle: dict | None) -> dict:
    """Pronóstico para el día siguiente al último día con datos.

    bundle = lo que guarda ml/entrenar.py (modelo + metadatos). Si es None se usa persistencia.
    """
    dia = features_diarias(df_horario)
    validos = dia.dropna(subset=["pm_escolar"])
    if validos.empty:
        raise ValueError("La serie no tiene ningún día con suficientes horas escolares")
    ultimo = validos.iloc[[-1]]
    fecha_base: date = ultimo.index[0].date()
    hoy_pm = float(ultimo["pm_escolar"].iloc[0])

    if bundle is not None:
        X = ultimo[bundle["features"]]
        pm_manana = float(bundle["modelo"].predict(X)[0])
        fuente = "modelo"
    else:
        pm_manana = hoy_pm
        fuente = "persistencia"

    return armar_respuesta(fecha_base, hoy_pm, max(0.0, pm_manana), fuente,
                           bundle.get("metricas") if bundle else None)


def armar_respuesta(fecha_base: date, hoy_pm: float | None, manana_pm: float | None, fuente: str,
                    metricas: dict | None = None) -> dict:
    def dia(nombre: str, pm: float | None, fecha: date) -> dict:
        n = nivel(pm) or {}
        return {"dia": nombre, "fecha": fecha.isoformat(), "pm": None if pm is None else int(round(pm)),
                "semaforo": n.get("semaforo"), "nivel": n.get("id"), "nombre": n.get("nombre"),
                "consejo": n.get("consejo")}

    return {
        "fuente": fuente,  # modelo | persistencia | sensor (persistencia con el nodo de afuera)
        "fecha_base": fecha_base.isoformat(),
        "dias": [dia("Hoy", hoy_pm, fecha_base), dia("Mañana", manana_pm, fecha_base + timedelta(days=1))],
        "metricas_modelo": metricas,
        "nota": "Promedio de PM2.5 de 7:00 a 14:00. Orienta; no sustituye avisos oficiales.",
    }


def cargar_bundle(path: Path):
    if not Path(path).exists():
        return None
    import joblib

    return joblib.load(path)


def pronostico_actual(conn, cfg) -> dict | None:
    """Lo que usa la API. Orden de respaldo (plan B del roadmap):
    1. modelo entrenado + serie del SIMAJ
    2. persistencia con la serie del SIMAJ
    3. persistencia con el promedio de hoy del sensor de afuera
    4. None (no hay con qué pronosticar)
    """
    from app import db

    if Path(cfg.serie_simaj).exists():
        try:
            serie = cargar_serie(cfg.serie_simaj, cfg.estacion_referencia)
            bundle = cargar_bundle(cfg.modelo_path)
            if bundle is not None and bundle.get("estacion", "").casefold() != cfg.estacion_referencia.casefold():
                bundle = None  # el modelo se entrenó con otra estación
            r = predecir_desde_serie(serie, bundle)
            r["estacion"] = cfg.estacion_referencia
            # Si la serie no se ha actualizado, "Hoy" es en realidad el último día con datos
            r["desactualizado"] = (db.ahora().date() - date.fromisoformat(r["fecha_base"])).days > 1
            return r
        except Exception as exc:  # serie corrupta o incompleta: se cae al sensor
            error = str(exc)
    else:
        error = f"no existe {cfg.serie_simaj}"

    hoy = db.ahora()
    inicio = hoy.replace(hour=min(HORAS_ESCUELA), minute=0, second=0)
    fin = hoy.replace(hour=max(HORAS_ESCUELA), minute=59, second=59)
    fila = conn.execute(
        "SELECT AVG(pm25) AS p FROM lecturas WHERE ubicacion='fuera' AND ts BETWEEN ? AND ?",
        (inicio.isoformat(), fin.isoformat()),
    ).fetchone()
    if fila["p"] is None:
        return None
    r = armar_respuesta(hoy.date(), float(fila["p"]), float(fila["p"]), "sensor")
    r["aviso"] = f"Sin serie del SIMAJ ({error}); se usa persistencia con el sensor de afuera."
    return r

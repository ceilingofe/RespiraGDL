"""Entrena y evalúa el pronóstico de PM2.5 de mañana (promedio 7:00–14:00).

    python ml/entrenar.py --estacion Miravalle
    python ml/entrenar.py --estacion Miravalle --corte 2025-07-01     # fecha donde empieza la prueba
    python ml/entrenar.py --sintetico                                # SOLO para probar el código

Salidas:
    ml/modelos/pronostico_pm25.joblib     modelo + variables + métricas (lo carga la API)
    ml/resultados/metricas.json           números para el reporte
    ml/resultados/metodo_resultados.md    tabla lista para pegar en la sección de método
    ml/resultados/pred_vs_real.png        gráfica de la prueba (si hay matplotlib)

Método:
    * Partición TEMPORAL (sin revolver): entrenar con días antes de --corte, probar después.
      Por defecto el último 20 % de los días es la prueba.
    * Línea base: persistencia (mañana = hoy).
    * Modelo: HistGradientBoostingRegressor (acepta huecos en clima sin imputar).
    * Métricas: MAE y RMSE en µg/m³, y % de días con el color del semáforo correcto.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from app.core.pronostico import FEATURES, cargar_serie, features_diarias  # noqa: E402
from app.core.semaforo import semaforo  # noqa: E402


def serie_sintetica(dias: int = 900, semilla: int = 0) -> pd.DataFrame:
    """Serie FALSA con estacionalidad (secas invierno-primavera) y ciclo diario. Solo para pruebas."""
    rng = np.random.default_rng(semilla)
    idx = pd.date_range("2023-01-01", periods=dias * 24, freq="h")
    doy, hora = idx.dayofyear.to_numpy(), idx.hour.to_numpy()
    estacional = 28 + 14 * np.cos(2 * np.pi * (doy - 20) / 365)
    diario = 10 * np.exp(-((hora - 9) ** 2) / 6) + 4 * np.exp(-((hora - 21) ** 2) / 8)
    # componente persistente de varios días (episodios de contaminación)
    episodios = np.repeat(pd.Series(rng.normal(0, 8, dias)).rolling(3, min_periods=1).mean().to_numpy(), 24)
    tmp = 20 + 6 * np.sin(2 * np.pi * (hora - 9) / 24) - 4 * np.cos(2 * np.pi * (doy - 20) / 365)
    vv = np.clip(rng.gamma(2, 1.2, len(idx)), 0, None)
    pm = estacional + diario + episodios - 1.5 * vv + rng.normal(0, 4, len(idx))
    df = pd.DataFrame({"fecha_hora": idx, "estacion": "Sintética", "pm25": np.clip(pm, 2, None), "tmp": tmp,
                       "hr": 50 + rng.normal(0, 10, len(idx)), "vv": vv})
    df.loc[rng.random(len(df)) < 0.05, "pm25"] = np.nan  # 5 % de huecos como en la vida real
    return df


def metricas(y: pd.Series, pred: pd.Series) -> dict:
    err = pred - y
    colores_ok = np.mean([semaforo(a) == semaforo(b) for a, b in zip(y, pred, strict=True)])
    alerta_real = np.array([semaforo(v) != "verde" for v in y])
    alerta_pred = np.array([semaforo(v) != "verde" for v in pred])
    detectadas = (alerta_real & alerta_pred).sum() / max(alerta_real.sum(), 1)
    falsas = (~alerta_real & alerta_pred).sum() / max(alerta_pred.sum(), 1)
    return {
        "mae": round(float(np.mean(np.abs(err))), 2),
        "rmse": round(float(np.sqrt(np.mean(err ** 2))), 2),
        "acierto_semaforo_pct": round(100 * float(colores_ok), 1),
        "dias_amarillo_o_rojo_detectados_pct": round(100 * float(detectadas), 1),
        "falsas_alarmas_pct": round(100 * float(falsas), 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=RAIZ / "data" / "processed" / "simaj_horario.csv")
    ap.add_argument("--estacion", default="Miravalle")
    ap.add_argument("--corte", type=lambda s: pd.Timestamp(s), help="primer día del periodo de prueba")
    ap.add_argument("--sintetico", action="store_true", help="usa datos FALSOS para probar el código")
    ap.add_argument("--modelo", type=Path, default=RAIZ / "ml" / "modelos" / "pronostico_pm25.joblib")
    ap.add_argument("--resultados", type=Path, default=RAIZ / "ml" / "resultados")
    args = ap.parse_args()

    from sklearn.ensemble import HistGradientBoostingRegressor
    import joblib

    if args.sintetico:
        horario, estacion = serie_sintetica(), "Sintética"
        print("AVISO: datos SINTÉTICOS. Estos números NO van al reporte.")
    else:
        horario, estacion = cargar_serie(args.datos, args.estacion), args.estacion

    dia = features_diarias(horario).dropna(subset=["y", "pm_escolar"])
    if len(dia) < 120:
        raise SystemExit(f"Solo hay {len(dia)} días útiles; se necesitan al menos ~120 para entrenar y probar.")
    corte = args.corte or dia.index[int(len(dia) * 0.8)]
    ent, pru = dia[dia.index < corte], dia[dia.index >= corte]
    print(f"Estación {estacion}: {len(dia)} días útiles · entrenamiento {ent.index.min().date()} a "
          f"{ent.index.max().date()} ({len(ent)}) · prueba {pru.index.min().date()} a {pru.index.max().date()} "
          f"({len(pru)})")

    modelo = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                           min_samples_leaf=20, l2_regularization=1.0, random_state=0)
    modelo.fit(ent[FEATURES], ent["y"])
    pred_modelo = pd.Series(np.clip(modelo.predict(pru[FEATURES]), 0, None), index=pru.index)
    pred_base = pru["pm_escolar"]  # persistencia

    m_modelo, m_base = metricas(pru["y"], pred_modelo), metricas(pru["y"], pred_base)
    mejora = round(100 * (1 - m_modelo["mae"] / m_base["mae"]), 1) if m_base["mae"] else 0.0
    usar_modelo = m_modelo["mae"] < m_base["mae"]
    print(f"Persistencia: {m_base}\nModelo:       {m_modelo}\nMejora en MAE: {mejora} %")

    resultado = {
        "estacion": estacion,
        "sintetico": args.sintetico,
        "generado": datetime.now().isoformat(timespec="seconds"),
        "dias_entrenamiento": len(ent), "dias_prueba": len(pru),
        "periodo_entrenamiento": [str(ent.index.min().date()), str(ent.index.max().date())],
        "periodo_prueba": [str(pru.index.min().date()), str(pru.index.max().date())],
        "persistencia": m_base, "modelo": m_modelo, "mejora_mae_pct": mejora,
        "se_usa": "modelo" if usar_modelo else "persistencia",
        "variables": FEATURES,
    }
    args.resultados.mkdir(parents=True, exist_ok=True)
    sufijo = "_sintetico" if args.sintetico else ""
    (args.resultados / f"metricas{sufijo}.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2),
                                                         encoding="utf-8")
    (args.resultados / f"metodo_resultados{sufijo}.md").write_text(tabla_md(resultado), encoding="utf-8")
    grafica(pru["y"], pred_modelo, pred_base, args.resultados / f"pred_vs_real{sufijo}.png", estacion)

    if args.sintetico:
        print("No se guarda el modelo porque los datos son sintéticos.")
    elif usar_modelo:
        args.modelo.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"modelo": modelo, "features": FEATURES, "estacion": estacion,
                     "metricas": {"mae": m_modelo["mae"], "mae_persistencia": m_base["mae"],
                                  "acierto_semaforo_pct": m_modelo["acierto_semaforo_pct"]}}, args.modelo)
        print(f"Modelo guardado en {args.modelo}")
    else:
        print("El modelo NO le gana a la persistencia: no se guarda; la API usará persistencia (plan B).")
    print(f"Resultados en {args.resultados}")


def tabla_md(r: dict) -> str:
    p, m = r["persistencia"], r["modelo"]
    aviso = "\n> ⚠️ Datos SINTÉTICOS: solo prueba del código. No usar en el reporte.\n" if r["sintetico"] else ""
    return f"""## Resultados del pronóstico (estación {r['estacion']}){aviso}

Entrenamiento: {r['periodo_entrenamiento'][0]} a {r['periodo_entrenamiento'][1]} ({r['dias_entrenamiento']} días).
Prueba: {r['periodo_prueba'][0]} a {r['periodo_prueba'][1]} ({r['dias_prueba']} días), sin mezclar con el entrenamiento.
Objetivo: PM2.5 promedio de mañana de 7:00 a 14:00 (µg/m³).

| Métrica | Persistencia (mañana = hoy) | Modelo (gradient boosting) |
| --- | --- | --- |
| Error absoluto medio (MAE, µg/m³) | {p['mae']} | {m['mae']} |
| Raíz del error cuadrático medio (RMSE, µg/m³) | {p['rmse']} | {m['rmse']} |
| Días con el color del semáforo correcto | {p['acierto_semaforo_pct']} % | {m['acierto_semaforo_pct']} % |
| Días amarillo/rojo que se avisaron | {p['dias_amarillo_o_rojo_detectados_pct']} % | {m['dias_amarillo_o_rojo_detectados_pct']} % |
| Avisos que resultaron falsa alarma | {p['falsas_alarmas_pct']} % | {m['falsas_alarmas_pct']} % |

Mejora del modelo sobre la persistencia en MAE: **{r['mejora_mae_pct']} %**. En la demo se usa: **{r['se_usa']}**.
"""


def grafica(y, pred_m, pred_b, ruta: Path, estacion: str) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=150)
    ax.plot(y.index, y, color="#1f2937", lw=1.4, label="Real")
    ax.plot(pred_m.index, pred_m, color="#2563eb", lw=1.2, label="Modelo")
    ax.plot(pred_b.index, pred_b, color="#9ca3af", lw=1, ls="--", label="Persistencia")
    for lim in (33, 79):
        ax.axhline(lim, color="#d1d5db", lw=0.8)
    ax.set_ylabel("PM2.5 7:00–14:00 (µg/m³)")
    ax.set_title(f"Pronóstico a 24 h · estación {estacion} · periodo de prueba", loc="left", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncols=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


if __name__ == "__main__":
    main()

"""Render the branded historical holdout chart from exported test predictions.

Run from any directory: python ml/graficar_resultados.py
Install plotting support with: pip install -r ml/requirements-grafica.txt
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
from matplotlib import font_manager
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def render(predictions: Path, output: Path) -> dict:
    """Plot outcomes on target dates and preserve gaps in the evaluated series."""
    tokens = dict(re.findall(
        r"--rg-([\w-]+):\s*(#[0-9a-fA-F]{6})",
        (ROOT / "frontend/src/styles/tokens.css").read_text(encoding="utf-8"),
    ))
    for name in ("Poppins-Regular.ttf", "Poppins-SemiBold.ttf"):
        font_manager.fontManager.addfont(str(ROOT / "entregables/assets" / name))
    plt.rcParams.update({
        "font.family": "Poppins", "font.size": 10, "text.color": tokens["ink"],
        "axes.labelcolor": tokens["ink"], "xtick.color": tokens["muted"],
        "ytick.color": tokens["muted"], "axes.edgecolor": tokens["sage"],
    })
    data = pd.read_csv(predictions, parse_dates=["fecha"]).set_index("fecha").sort_index()
    required = ["pm_escolar", "y", "prediction"]
    if data.empty or data.index.has_duplicates or data[required].isna().any().any():
        raise ValueError("Predictions must contain unique dates and complete observed, model, and persistence values.")
    model_mae = round(float((data["y"] - data["prediction"]).abs().mean()), 2)
    persistence_mae = round(float((data["y"] - data["pm_escolar"]).abs().mean()), 2)
    improvement = round(100 * (1 - model_mae / persistence_mae), 1) if persistence_mae else 0.0
    evaluated_days = len(data)
    data.index = data.index + pd.Timedelta(days=1)
    first_year, last_year = data.index.min().year, data.index.max().year
    start, end = pd.Timestamp(first_year, 1, 1), pd.Timestamp(last_year, 12, 31)
    years = str(first_year) if first_year == last_year else f"{first_year}–{last_year}"
    data = data.reindex(pd.date_range(start, end, freq="D"))

    fig, ax = plt.subplots(figsize=(12, 5.3), dpi=180)
    fig.patch.set_facecolor(tokens["white"])
    ax.set_facecolor(tokens["white"])
    ax.plot(data.index, data["y"], color=tokens["ink"], linewidth=1.2, alpha=.85,
            label="Observado", marker=".", markersize=2.2, zorder=3)
    ax.plot(data.index, data["prediction"], color=tokens["teal"], linewidth=1.8,
            label=f"Modelo · MAE {model_mae:.2f} µg/m³", zorder=4)
    ax.plot(data.index, data["pm_escolar"], color=tokens["muted"], linewidth=1.1,
            linestyle=(0, (3, 2)), alpha=.75,
            label=f"Persistencia · MAE {persistence_mae:.2f} µg/m³", zorder=2)
    ax.set_ylim(bottom=0)
    ax.set_xlim(start, end)
    ax.set_ylabel("PM2.5 escolar, 7:00–14:00 (µg/m³)", labelpad=10)
    ax.set_xlabel(f"Fecha del promedio observado / pronosticado ({years})", labelpad=12)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda value, _: months[mdates.num2date(value).month - 1],
    ))
    ax.grid(axis="y", color=tokens["sage"], linewidth=.6, alpha=.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.text(.09, .95, "Miravalle · pronóstico histórico del día siguiente", fontsize=15, weight="semibold")
    fig.text(.09, .90,
             f"{evaluated_days} días de prueba de {years} · mejora del MAE: {improvement:.1f} %",
             fontsize=10, color=tokens["muted"])
    fig.text(.09, .035,
             "Fuente: SIMAJ / SEMADET. Huecos sin evaluación se dejan vacíos. Sin validación clínica.",
             fontsize=9, color=tokens["muted"])
    fig.subplots_adjust(left=.09, right=.98, bottom=.19, top=.83)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, facecolor=tokens["white"])
    plt.close(fig)
    return {
        "evaluated_days": evaluated_days, "model_mae": model_mae,
        "persistence_mae": persistence_mae, "improvement_mae_pct": improvement,
        "source_sha256": hashlib.sha256(predictions.read_bytes()).hexdigest(),
        "plot_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "matplotlib_version": matplotlib.__version__,
        "x_axis": "Target day (predictor day plus one calendar day)",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predicciones", type=Path, default=ROOT / "ml/resultados/predicciones_prueba.csv")
    parser.add_argument("--salida", type=Path, default=ROOT / "ml/resultados/pred_vs_real.png")
    args = parser.parse_args()
    print(json.dumps(render(args.predicciones, args.salida), indent=2))


if __name__ == "__main__":
    main()

"""La entrega recarga el modelo real y reproduce la evaluación publicada."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from app.core.pronostico import cargar_bundle, cargar_serie, features_diarias


def test_modelo_entregado_reproduce_las_predicciones_y_mae_publicados():
    raiz = Path(__file__).resolve().parents[2]
    metricas = json.loads((raiz / "ml/resultados/metricas.json").read_text(encoding="utf-8"))
    guardadas = pd.read_csv(raiz / "ml/resultados/predicciones_prueba.csv", parse_dates=["fecha"]).set_index("fecha")
    modelo = cargar_bundle(raiz / "ml/modelos/pronostico_pm25.joblib")
    serie = cargar_serie(raiz / "data/processed/simaj_horario.csv", "Miravalle")
    dias = features_diarias(serie).loc[guardadas.index]
    predicciones = np.clip(modelo["modelo"].predict(dias[modelo["features"]]), 0, None)
    assert len(guardadas) == metricas["dias_prueba"]
    assert np.allclose(dias["y"], guardadas["y"], rtol=1e-8, atol=1e-8)
    assert np.allclose(predicciones, guardadas["prediction"], rtol=1e-8, atol=1e-8)
    assert round(float(np.mean(np.abs(predicciones - dias["y"].to_numpy()))), 2) == metricas["modelo"]["mae"]

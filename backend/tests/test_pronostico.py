"""Pruebas del pronóstico con datos sintéticos (solo prueban el código, no el desempeño)."""
import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")
pytest.importorskip("sklearn")

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ml"))

from entrenar import serie_sintetica  # noqa: E402

from app import db  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.core.pronostico import FEATURES, features_diarias, predecir_desde_serie, pronostico_actual  # noqa: E402


def test_features_sin_fuga_de_informacion():
    dia = features_diarias(serie_sintetica(60))
    # el objetivo de hoy es el promedio escolar de mañana, nunca el de hoy
    validos = dia.dropna(subset=["y"])
    assert (validos["y"].iloc[:-1].to_numpy() == dia["pm_escolar"].shift(-1).loc[validos.index].iloc[:-1]
            .to_numpy()).all()
    assert set(FEATURES) <= set(dia.columns)


def test_persistencia():
    r = predecir_desde_serie(serie_sintetica(30), None)
    hoy, manana = r["dias"]
    assert r["fuente"] == "persistencia" and hoy["pm"] == manana["pm"]
    assert manana["semaforo"] in ("verde", "amarillo", "rojo")


def _preparar_serie_y_modelo(tmp_path, monkeypatch):
    """Serie sintética (termina en 2023, o sea desactualizada) + modelo entrenado con ella."""
    import joblib
    from sklearn.ensemble import HistGradientBoostingRegressor

    serie = serie_sintetica(200)
    dia = features_diarias(serie).dropna(subset=["y", "pm_escolar"])
    modelo = HistGradientBoostingRegressor(max_iter=20).fit(dia[FEATURES], dia["y"])
    joblib.dump({"modelo": modelo, "features": FEATURES, "estacion": "Sintética", "metricas": {"mae": 1}},
                tmp_path / "m.joblib")
    serie.to_csv(tmp_path / "s.csv", index=False)
    monkeypatch.setenv("MODELO_PATH", str(tmp_path / "m.joblib"))
    monkeypatch.setenv("SERIE_SIMAJ", str(tmp_path / "s.csv"))
    monkeypatch.setenv("ESTACION_REFERENCIA", "Sintética")


def test_con_modelo(tmp_path, monkeypatch):
    _preparar_serie_y_modelo(tmp_path, monkeypatch)
    with db.conexion() as conn:
        r = pronostico_actual(conn, get_settings())
    assert r["fuente"] == "modelo" and r["dias"][1]["pm"] >= 0


def test_sensor_manda_si_serie_desactualizada(tmp_path, monkeypatch):
    _preparar_serie_y_modelo(tmp_path, monkeypatch)
    with db.conexion() as conn:
        db.insertar_lectura(conn, nodo_id="esc-mir-fuera", escuela="miravalle", salon_id=None,
                            ubicacion="fuera", pm25=40, ts=db.ahora().replace(hour=10, minute=0, second=0))
        r = pronostico_actual(conn, get_settings())
    assert r["fuente"] == "sensor" and r["desactualizado"] is False
    assert r["dias"][0]["dia"] == "Hoy" and r["dias"][0]["pm"] == 40 and r["dias"][1]["pm"] == 40
    assert r["modelo_evaluado"] == {"mae": 1}  # el modelo existe y se reporta aunque no se use
    assert "desactualizada" in r["aviso"]


def test_serie_desactualizada_sin_sensor(tmp_path, monkeypatch):
    _preparar_serie_y_modelo(tmp_path, monkeypatch)
    with db.conexion() as conn:
        r = pronostico_actual(conn, get_settings())
    assert r["fuente"] == "modelo" and r["desactualizado"] is True
    assert [d["dia"] for d in r["dias"]] == ["Último dato", "Día siguiente"]
    assert r["dias"][0]["fecha"] == r["fecha_base"]  # la fecha real del dato, no la de hoy

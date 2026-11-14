"""Pruebas del importador de la base histórica del SIMAJ (data/scripts/importar_simaj.py)."""
import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "data" / "scripts"))

from importar_simaj import ESTACIONES, PARAMETROS, normalizar  # noqa: E402


def _hoja_data():
    """Mini hoja "Data" con el mismo formato real de BD_<año>.xlsx."""
    return pd.DataFrame({
        "STATION": ["MIR", "MIR", "PIN", "SFE", "CEN", "AGU"],
        "DATE": pd.to_datetime(["2024-01-01 00:00", "2024-01-01 01:00", "2024-01-01 00:00",
                                "2024-01-01 00:00", "2024-01-01 00:00", "2024-01-01 00:00"]),
        "HOUR": [0, 1, 0, 0, 0, 0],
        "DIA": ["=DAY(B2)"] * 6,     # columnas de fórmula que traen los libros 2023-2024
        "MES ": ["=MONTH(B2)"] * 6,
        "O3": [0.012, 0.010, None, 0.02, 0.01, 0.01],
        "PM2.5": [41.0, "IF", 12.5, None, 30.0, 99.0],   # bandera de texto y vacío -> fuera
        "PM10": [80.0, None, 20.0, 51.0, 50.0, 88.0],
        "IT": [21.0, 21.1, 20.0, 19.5, 20.2, 20.0],
        "ET": [18.2, 19.0, None, 17.0, 16.5, 15.0],
        "RH": [55, 60, 50, 40, 45, 42],
        "WS": [1.2, 0.8, 2.0, 1.0, 0.5, 0.7],
        "WD": [120, "IO", 90, 45, 10, 300],
    })


def test_estaciones_y_parametros():
    assert ESTACIONES == {"MIR": ("Miravalle", 106), "CEN": ("Centro", 102),
                          "PIN": ("Las Pintas", 104), "SFE": ("Santa Fe", 108)}
    # ET (temperatura externa) se publica como TMP; WD/IT/O3 no se importan
    assert PARAMETROS == {"PM2.5": "PM2.5", "PM10": "PM10", "ET": "TMP", "RH": "HR", "WS": "VV"}


def test_normalizar():
    r = normalizar(_hoja_data())
    assert list(r.columns) == ["estacion", "estacion_id", "parametro", "fecha", "hora", "valor", "valido"]
    # AGU no es de las nuestras; O3, IT y WD no se importan
    assert set(r["estacion"]) == {"Miravalle", "Las Pintas", "Santa Fe", "Centro"}
    assert set(r["parametro"]) == {"PM2.5", "PM10", "TMP", "HR", "VV"}
    # la bandera "IF" y la celda vacía de PM2.5 se descartan
    pm = r[r["parametro"] == "PM2.5"].set_index("estacion")["valor"]
    assert pm.to_dict() == {"Miravalle": 41.0, "Las Pintas": 12.5, "Centro": 30.0}
    # ids de SINAICA y fecha/hora en el formato del pipeline
    assert r[r["estacion"] == "Las Pintas"]["estacion_id"].unique().tolist() == [104]
    assert (r["fecha"] == "2024-01-01").all() and set(r["hora"]) == {0, 1}
    assert (r["valido"] == 1).all()


def test_normalizar_compatible_con_procesar():
    """La salida se puede limpiar con procesar_sinaica.limpiar sin cambios."""
    sys.path.insert(0, str(RAIZ / "data" / "scripts"))
    from procesar_sinaica import limpiar

    ancho = limpiar(normalizar(_hoja_data()))
    assert {"fecha_hora", "estacion", "pm25", "pm10", "tmp", "hr", "vv"} <= set(ancho.columns)
    mir = ancho[ancho["estacion"] == "Miravalle"].set_index("fecha_hora")
    assert mir.loc["2024-01-01 00:00", "pm25"] == 41.0

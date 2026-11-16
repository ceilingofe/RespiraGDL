"""Los huecos largos no deben convertirse parcialmente en observaciones imputadas."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data" / "scripts"))
from procesar_sinaica import limpiar


def serie(valores):
    return pd.DataFrame({
        "estacion": ["Miravalle"] * len(valores),
        "fecha": ["2024-01-01"] * len(valores),
        "hora": list(range(len(valores))),
        "parametro": ["PM2.5"] * len(valores),
        "valor": valores,
    })


def test_hueco_de_cuatro_horas_se_conserva_completo():
    resultado = limpiar(serie([10, None, None, None, None, 60]))
    assert resultado["pm25"].iloc[1:5].isna().all()
    assert resultado["pm25"].iloc[[0, 5]].tolist() == [10, 60]


def test_hueco_interior_de_tres_horas_se_interpola():
    resultado = limpiar(serie([10, None, None, None, 50]))
    assert resultado["pm25"].tolist() == [10, 20, 30, 40, 50]


def test_serie_de_dos_horas_no_falla_ni_extrapola():
    resultado = limpiar(serie([10, 20]))
    assert resultado["pm25"].tolist() == [10, 20]


def test_no_rellena_una_variable_sin_dos_extremos_validos():
    datos = pd.concat([serie([10, 20, 30, 40]),
                       serie([5, None, None, None]).assign(parametro="PM10")])
    resultado = limpiar(datos)
    assert resultado["pm10"].iloc[0] == 5
    assert resultado["pm10"].iloc[1:].isna().all()


def test_no_usa_el_dia_objetivo_para_imputar_el_dia_predictor():
    fechas = pd.date_range("2024-01-01 22:00", periods=4, freq="h")
    datos = pd.DataFrame({"estacion": "Miravalle", "fecha": fechas.strftime("%Y-%m-%d"),
                          "hora": fechas.hour, "parametro": "PM2.5", "valor": [10, None, None, 40]})
    resultado = limpiar(datos)
    assert resultado["pm25"].iloc[1:3].isna().all()
    assert resultado["pm25"].iloc[[0, 3]].tolist() == [10, 40]

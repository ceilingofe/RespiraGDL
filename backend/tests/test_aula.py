import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.services import aula


def test_proteccion_render_del_plan():
    assert aula.proteccion(62, 21) == 66
    assert aula.proteccion(0, 10) is None


def test_niveles():
    assert aula.nivel(20)["id"] == "good"
    assert aula.nivel(45)["id"] == "ok"
    assert aula.nivel(62)["nombre"] == "Mala"
    assert aula.nivel(200)["id"] == "ext"


def test_filtro_apagado_es_lo_primero():
    r = aula.recomendaciones(62, 55, filtro=False, asma=1)
    assert r[0]["prioridad"] == "alta" and "filtro" in r[0]["texto"]
    assert any("el alumno con asma" in x["texto"] for x in r)


def test_filtro_viejo():
    r = aula.recomendaciones(30, 10, filtro_cambio=date(2026, 7, 1), hoy=date(2026, 11, 14))
    assert any("MERV-13" in x["texto"] for x in r)


def test_endpoint_estado():
    d = TestClient(app).get("/aula/estado", params={"fuera": 62, "dentro": 21, "asma": 4}).json()
    assert d["proteccion_pct"] == 66
    assert d["fuera"]["id"] == "bad" and d["dentro"]["id"] == "good"
    assert d["recomendaciones"][0]["prioridad"] in {"alta", "media"}

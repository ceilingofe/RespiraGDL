"""Pruebas de los endpoints. Corren en CI (requirements.txt instala FastAPI y httpx)."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_flujo_completo(client):
    assert client.post("/salones", json={"id": "3b", "escuela": "Miravalle", "grupo": "3° B",
                                         "alumnos_asma": 5}).status_code == 201
    r = client.post("/lecturas", json={"nodo_id": "esc-miravalle-salon-3B-fuera", "pm25": 62, "pm10": 80})
    assert r.status_code == 201 and r.json()["ubicacion"] == "fuera"
    client.post("/lecturas", json={"nodo_id": "esc-miravalle-salon-3B-dentro", "pm25": 21})

    p = client.get("/salones/3B/proteccion").json()
    assert p["proteccion_pct"] == 66 and p["estado"] == "ok"

    salones = client.get("/salones").json()
    assert salones[0]["id"] == "3B" and salones[0]["asma"] == 5

    serie = client.get("/lecturas/serie", params={"salon_id": "3B"}).json()
    assert isinstance(serie, list)

    nodos = client.get("/lecturas/nodos").json()
    assert len(nodos) == 2


def test_lectura_invalida(client):
    assert client.post("/lecturas", json={"nodo_id": "nodo-raro", "pm25": 10}).status_code == 422
    assert client.post("/lecturas", json={"nodo_id": "esc-a-fuera", "pm25": -1}).status_code == 422


def test_token(client, monkeypatch):
    monkeypatch.setenv("NODO_TOKEN", "secreto")
    cuerpo = {"nodo_id": "esc-miravalle-fuera", "pm25": 30}
    assert client.post("/lecturas", json=cuerpo).status_code == 401
    assert client.post("/lecturas", json=cuerpo, headers={"X-Nodo-Token": "secreto"}).status_code == 201


def test_pronostico_y_alertas_sin_datos(client):
    assert client.get("/pronostico").status_code == 503
    hoy = client.get("/alertas/hoy").json()
    assert hoy["nivel"] is None and hoy["alertas"] == []


def test_pronostico_con_sensor(client):
    client.post("/lecturas", json={"nodo_id": "esc-miravalle-fuera", "pm25": 62})
    r = client.get("/pronostico")
    # fuera del horario escolar el sensor no cuenta para el pronóstico
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        assert r.json()["fuente"] == "sensor"


def test_salon_inexistente(client):
    assert client.get("/salones/9Z/proteccion").status_code == 404

"""Endpoints nuevos con el contrato del bot y del frontend de Carlos. Corren en CI."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_contrato_bot_avisos(client):
    r = client.post("/alertas/aviso", json={"escuela_id": "miravalle", "texto": "Recreo adentro", "grupo": "3A"})
    assert r.status_code == 201
    aviso = r.json()
    assert {"id", "escuela_id", "grupo", "texto", "creado"} <= set(aviso)
    client.post("/alertas/aviso", json={"escuela_id": "miravalle", "texto": "Para toda la escuela"})
    pend = client.get("/alertas/aviso/pendientes", params={"escuela_id": "miravalle"}).json()
    assert [p["grupo"] for p in pend] == ["3A", None]
    r = client.post(f"/alertas/aviso/{aviso['id']}/enviado", json={"familias": 12})
    assert r.status_code == 200 and r.json()["familias"] == 12
    assert len(client.get("/alertas/aviso/pendientes", params={"escuela_id": "miravalle"}).json()) == 1
    assert client.post("/alertas/aviso/999/enviado", json={"familias": 1}).status_code == 404
    assert client.post("/alertas/aviso", json={"escuela_id": "miravalle", "texto": ""}).status_code == 422


def test_enviar_desde_tablero(client):
    r = client.post("/alertas/enviar", json={"mensaje": "Mañana aire malo"})
    assert r.status_code == 201 and r.json()["escuela_id"] == "miravalle" and r.json()["grupo"] is None
    r = client.post("/alertas/enviar")  # sin cuerpo: usa el texto sugerido
    assert r.status_code == 201 and "inhalador" in r.json()["texto"]
    assert "texto" in client.get("/alertas/mensaje-familias").json()


def test_programacion(client):
    assert client.get("/alertas/programacion").json()["hora"] == "07:00"
    assert client.put("/alertas/programacion", json={"hora": "06:30", "mensaje": "x"}).json()["hora"] == "06:30"
    assert client.get("/alertas/programacion").json()["hora"] == "06:30"
    assert client.put("/alertas/programacion", json={"hora": "6:30"}).status_code == 422


def test_suscripciones_y_reportes(client):
    r = client.post("/suscripciones", json={"chat_id": 555, "grupos": ["3a"]})
    assert r.status_code == 201 and r.json() == {"chat_id": "555", "escuela_id": "miravalle", "grupos": ["3A"]}
    assert len(client.get("/suscripciones", params={"grupo": "3A"}).json()) == 1
    assert client.delete("/suscripciones/555").status_code == 200
    assert client.delete("/suscripciones/555").status_code == 404
    assert client.post("/reportes-sintomas", json={"escuela": "miravalle"}).json() == {"total_hoy": 1}
    client.post("/reportes-sintomas", json={"escuela_id": "miravalle", "grupo": "3A"})
    hoy = client.get("/reportes-sintomas/hoy").json()
    assert hoy["total"] == 2


def test_pantallas(client):
    client.post("/salones", json={"id": "3A", "escuela": "miravalle", "grupo": "3° A", "alumnos_asma": 4})
    client.post("/lecturas", json={"nodo_id": "esc-miravalle-fuera", "pm25": 62})
    client.post("/lecturas", json={"nodo_id": "esc-miravalle-salon-3A-dentro", "pm25": 19})

    e = client.get("/escuelas/miravalle").json()
    assert e["pm25Hoy"] == 62 and e["semaforoHoy"] == "amarillo" and e["nombreCorto"]
    assert client.get("/escuelas/no-existe").status_code == 404

    m = client.get("/salones/3A/hoy").json()
    assert m["titulo"] == "Maestra 3° A" and m["conAsma"] == 4 and m["pm25"] == 62
    t = client.post("/salones/3A/tareas/recreo").json()
    assert next(x for x in t if x["id"] == "recreo")["hecho"] is True
    assert client.post("/salones/3A/tareas/nada").status_code == 404

    assert isinstance(client.get("/lecturas", params={"salon": "3A", "fecha": "hoy"}).json(), list)
    assert client.get("/pronostico/manana").status_code in (200, 503)

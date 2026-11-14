import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import plan_asma
from app.services.semaforo import nivel, protocolo, mensaje_familias

c = TestClient(app)


@pytest.fixture(autouse=True)
def limpio():
    plan_asma._reiniciar()
    yield


@pytest.mark.parametrize("pm,esperado", [(0, "good"), (15, "good"), (16, "ok"), (33, "ok"), (62, "bad"), (79, "bad"), (95, "vbad"), (200, "ext")])
def test_cortes_del_semaforo(pm, esperado):
    assert nivel(pm)["id"] == esperado


def test_pm_negativo_falla():
    with pytest.raises(ValueError):
        nivel(-1)


def test_protocolo_aire_malo_mueve_recreo():
    p = protocolo(71)
    assert p["color"] == "amarillo"
    assert any("Recreo adentro" in t for t in p["maestro"])
    assert any("inhalador" in t for t in p["familias"])


def test_endpoint_protocolo():
    r = c.get("/plan-asma/protocolo", params={"pm25": 95})
    assert r.status_code == 200
    assert r.json()["id"] == "vbad"
    assert c.get("/plan-asma/protocolo", params={"pm25": -3}).status_code == 422


def test_niveles_tiene_cinco():
    assert [n["id"] for n in c.get("/plan-asma/niveles").json()] == ["good", "ok", "bad", "vbad", "ext"]


def test_incidente_anonimo_se_registra():
    r = c.post("/plan-asma/incidentes", json={"salon_id": "3A", "aviso_familia": True})
    assert r.status_code == 201
    fila = r.json()
    assert fila["salon_id"] == "3A" and fila["aviso_familia"] is True
    assert set(fila) == {"id", "fecha", "hora", "salon_id", "aviso_familia", "llamada_911"}
    ind = c.get("/plan-asma/indicadores").json()
    assert ind["crisis"] == 1 and ind["por_salon"] == {"3A": 1}


def test_incidente_rechaza_nombre_del_alumno():
    r = c.post("/plan-asma/incidentes", json={"salon_id": "3A", "nombre": "Ana"})
    assert r.status_code == 422
    assert c.get("/plan-asma/incidentes").json() == []


def test_escuelas_y_plan_de_manana():
    es = c.get("/escuelas").json()
    assert len(es) == 3
    assert c.get("/escuelas/las-pintas/plan-manana").json()["id"] == "vbad"
    assert c.get("/escuelas/no-existe/plan-manana").status_code == 404


def test_pronostico_y_mensaje():
    p = c.get("/alertas/pronostico").json()
    assert p[1]["nivel"]["nombre"] == "Mala"
    texto = mensaje_familias(71, "Miravalle")
    assert "MALA" in texto and "inhalador" in texto

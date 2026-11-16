"""Contrato del semáforo físico: no presentar simulación o datos viejos como actuales."""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture
def cliente():
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize("simulada", [False, True])
def test_semaforo_identifica_origen_de_las_lecturas(cliente, monkeypatch, simulada):
    ahora = datetime(2026, 11, 16, 10, 0)
    monkeypatch.setattr(db, "ahora", lambda: ahora)
    with db.conexion() as conn:
        db.insertar_lectura(conn, nodo_id="esc-miravalle-fuera", escuela="miravalle",
                            salon_id=None, ubicacion="fuera", pm25=62, ts=ahora,
                            simulada=simulada)
    datos = cliente.get("/alertas/hoy").json()
    assert datos["nivel"] == "amarillo"
    assert datos["simulado"] is simulada
    assert datos["desactualizado"] is False
    assert datos["fecha_base"] == "2026-11-16"
    assert datos["ultima_lectura"] == "2026-11-16T10:00:00"


def test_semaforo_no_confunde_dato_de_manana_temprano_con_sensor_actual(cliente, monkeypatch):
    ahora = datetime(2026, 11, 16, 10, 0)
    monkeypatch.setattr(db, "ahora", lambda: ahora)
    with db.conexion() as conn:
        db.insertar_lectura(conn, nodo_id="esc-miravalle-fuera", escuela="miravalle",
                            salon_id=None, ubicacion="fuera", pm25=20,
                            ts=ahora - timedelta(minutes=11))
    datos = cliente.get("/alertas/hoy").json()
    assert datos["desactualizado"] is True


def test_semaforo_sin_datos_declara_que_no_hay_vigencia(cliente):
    datos = cliente.get("/alertas/hoy").json()
    assert datos["nivel"] is None
    assert datos["desactualizado"] is True
    assert datos["simulado"] is False
    assert datos["fecha_base"] is None


def test_semaforo_preserva_antiguedad_del_historico(cliente, monkeypatch):
    from app.api import alertas
    from app.core.pronostico import armar_respuesta

    historico = armar_respuesta(datetime(2024, 12, 30).date(), 20, 22, "persistencia")
    historico["desactualizado"] = True
    monkeypatch.setattr(alertas, "pronostico_actual", lambda conn, cfg: historico)
    datos = cliente.get("/alertas/hoy").json()
    assert datos["desactualizado"] is True
    assert datos["fecha_base"] == "2024-12-30"
    assert datos["ultima_lectura"] is None

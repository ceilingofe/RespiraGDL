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


@pytest.mark.parametrize("edad,simulada,vencido", [(0, True, False), (11, False, True)])
def test_vista_maestra_conserva_procedencia_y_descarta_color_vencido(cliente, monkeypatch, edad, simulada, vencido):
    ahora = datetime(2026, 11, 16, 10, 0)
    monkeypatch.setattr(db, "ahora", lambda: ahora)
    with db.conexion() as conn:
        db.upsert_salon(conn, "3A", "miravalle", 4)
        db.insertar_lectura(conn, nodo_id="esc-miravalle-salon-3A-fuera", escuela="miravalle",
                            salon_id="3A", ubicacion="fuera", pm25=62,
                            ts=ahora - timedelta(minutes=edad), simulada=simulada)
    datos = cliente.get("/salones/3A/hoy").json()
    assert datos["simulado"] is simulada
    assert datos["desactualizado"] is vencido
    assert datos["ultima_lectura"] == (ahora - timedelta(minutes=edad)).isoformat()
    assert datos["semaforo"] == (None if vencido else "amarillo")
    assert datos["pm25"] == (None if vencido else 62)


def test_procedencia_maestra_corresponde_al_sensor_de_su_salon(cliente, monkeypatch):
    ahora = datetime(2026, 11, 16, 10, 0)
    monkeypatch.setattr(db, "ahora", lambda: ahora)
    with db.conexion() as conn:
        db.upsert_salon(conn, "3A", "miravalle", 4)
        for salon, simulada in [("3A", False), (None, True)]:
            db.insertar_lectura(conn, nodo_id=f"esc-miravalle-{salon or 'escuela'}-fuera",
                                escuela="miravalle", salon_id=salon, ubicacion="fuera",
                                pm25=62, ts=ahora, simulada=simulada)
    datos = cliente.get("/salones/3A/hoy").json()
    assert datos["simulado"] is False
    assert datos["desactualizado"] is False

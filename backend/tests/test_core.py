"""Pruebas de la lógica sin servidor (no necesitan FastAPI)."""
from datetime import datetime, timedelta

import pytest

from app import db
from app.config import get_settings
from app.core import estado
from app.core.nodos import parse_nodo_id
from app.core.proteccion import calcular_proteccion
from app.core.semaforo import nivel, semaforo


# ---------------------------------------------------------------- nodos
@pytest.mark.parametrize("nid, esperado", [
    ("esc-miravalle-salon-3B-dentro", ("miravalle", "3B", "dentro")),
    ("esc-miravalle-salon-3b-fuera", ("miravalle", "3B", "fuera")),
    ("esc-las-pintas-salon-1A-dentro", ("las-pintas", "1A", "dentro")),
    ("esc-santa-fe-fuera", ("santa-fe", None, "fuera")),
    ("ESC-Miravalle-Fuera", ("miravalle", None, "fuera")),
])
def test_parse_nodo(nid, esperado):
    n = parse_nodo_id(nid)
    assert (n.escuela, n.salon_id, n.ubicacion) == esperado


@pytest.mark.parametrize("nid", ["nodo1", "esc-miravalle-salon-3B", "esc-miravalle-dentro", ""])
def test_parse_nodo_invalido(nid):
    with pytest.raises(ValueError):
        parse_nodo_id(nid)


# ---------------------------------------------------------------- protección
def test_proteccion_render():
    # el render del plan: fuera 62, dentro 21 -> 66 %
    assert calcular_proteccion(62, 21) == {"proteccion_pct": 66, "estado": "ok"}


def test_proteccion_baja():
    assert calcular_proteccion(58, 41) == {"proteccion_pct": 29, "estado": "baja"}


def test_proteccion_casos_borde():
    assert calcular_proteccion(None, 20)["estado"] == "sin_datos"
    assert calcular_proteccion(30, None)["estado"] == "sin_datos"
    assert calcular_proteccion(6, 3) == {"proteccion_pct": None, "estado": "aire_limpio"}
    assert calcular_proteccion(40, 55)["proteccion_pct"] == 0      # dentro peor que fuera
    assert calcular_proteccion(40, 0)["proteccion_pct"] == 100


# ---------------------------------------------------------------- semáforo
@pytest.mark.parametrize("pm, nid, color", [
    (10, "good", "verde"), (15, "good", "verde"), (15.1, "ok", "verde"), (25, "ok", "verde"),
    (26, "bad", "amarillo"), (62, "bad", "amarillo"), (80, "vbad", "rojo"), (200, "ext", "rojo"),
])
def test_semaforo(pm, nid, color):
    assert nivel(pm)["id"] == nid and semaforo(pm) == color


def test_semaforo_sin_dato():
    assert nivel(None) is None and nivel(float("nan")) is None


# ---------------------------------------------------------------- estado y alertas
AHORA = datetime(2026, 11, 13, 10, 0, 0)


def _cargar(conn, filtro_ok=True):
    db.upsert_salon(conn, "3B", "miravalle", 5, True, "3° B")
    db.upsert_salon(conn, "5A", "miravalle", 6, True, "5° A")
    for m in range(0, 60, 5):
        t = AHORA - timedelta(minutes=m)
        db.insertar_lectura(conn, nodo_id="esc-miravalle-fuera", escuela="miravalle", salon_id=None,
                            ubicacion="fuera", pm25=58, ts=t)
        db.insertar_lectura(conn, nodo_id="esc-miravalle-salon-3B-dentro", escuela="miravalle",
                            salon_id="3B", ubicacion="dentro", pm25=21, ts=t)
        db.insertar_lectura(conn, nodo_id="esc-miravalle-salon-5A-dentro", escuela="miravalle",
                            salon_id="5A", ubicacion="dentro", pm25=41 if filtro_ok else 50, ts=t)


def test_estado_usa_sensor_de_escuela():
    with db.conexion() as conn:
        _cargar(conn)
        e = {s["id"]: s for s in estado.estados(conn, get_settings(), momento=AHORA)}
    assert e["3B"]["fuera"] == 58 and e["3B"]["dentro"] == 21 and e["3B"]["proteccion"] == 64
    assert e["3B"]["fuente_fuera"] == "sensor de la escuela"
    assert e["5A"]["estado"] == "baja"


def test_estado_prefiere_sensor_del_salon():
    with db.conexion() as conn:
        _cargar(conn)
        db.insertar_lectura(conn, nodo_id="esc-miravalle-salon-3B-fuera", escuela="miravalle",
                            salon_id="3B", ubicacion="fuera", pm25=70, ts=AHORA)
        e = estado.estado_salon(conn, db.obtener_salon(conn, "3B"), get_settings(), AHORA)
    assert e["fuera"] == 70 and e["fuente_fuera"] == "sensor del salón"


def test_alertas():
    pron = {"dias": [
        {"dia": "Hoy", "pm": 62, "semaforo": "amarillo"},
        {"dia": "Mañana", "pm": 85, "semaforo": "rojo", "nombre": "Muy mala", "consejo": "Recreo adentro."},
    ]}
    with db.conexion() as conn:
        _cargar(conn)
        # un nodo que dejó de mandar hace 30 min
        db.insertar_lectura(conn, nodo_id="esc-miravalle-salon-1A-dentro", escuela="miravalle",
                            salon_id="1A", ubicacion="dentro", pm25=20, ts=AHORA - timedelta(minutes=30))
        a = estado.alertas(conn, get_settings(), pron, momento=AHORA)
    tipos = [x["tipo"] for x in a]
    assert "proteccion_baja" in tipos and "sensor_desconectado" in tipos and "pronostico" in tipos
    assert a[0]["prioridad"] == "urgente"
    aviso = next(x for x in a if x["tipo"] == "pronostico")
    assert aviso["familias"] == 11
    baja = next(x for x in a if x["tipo"] == "proteccion_baja")
    assert baja["salon_id"] == "5A"


def test_alertas_sin_aviso_a_familias_si_pronostico_desactualizado():
    pron = {"desactualizado": True, "dias": [
        {"dia": "Último dato", "pm": 62, "semaforo": "amarillo"},
        {"dia": "Día siguiente", "pm": 85, "semaforo": "rojo", "nombre": "Muy mala", "consejo": "Recreo adentro."},
    ]}
    with db.conexion() as conn:
        _cargar(conn)
        a = estado.alertas(conn, get_settings(), pron, momento=AHORA)
    assert "pronostico" not in [x["tipo"] for x in a]


def test_serie_dia():
    with db.conexion() as conn:
        _cargar(conn)
        s = estado.serie_dia(conn, db.obtener_salon(conn, "3B"), AHORA)
    assert s and s[0]["h"] == "9:00" and s[-1] == {"h": "10:00", "fuera": 58, "dentro": 21}

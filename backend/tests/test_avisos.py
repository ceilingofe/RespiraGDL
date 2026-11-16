"""Avisos, suscripciones, reportes, programación y vistas de pantalla (lógica sin servidor)."""
from datetime import datetime, timedelta

import pytest

from app import db
from app.config import get_settings
from app.core import avisos as av
from app.core import escuela as esc

AHORA = datetime(2026, 11, 13, 10, 0, 0)  # viernes


def test_ciclo_de_aviso():
    with db.conexion() as conn:
        a = av.crear_aviso(conn, "Miravalle", "  Recreo adentro hoy  ", "3a")
        b = av.crear_aviso(conn, "miravalle", "Aviso general")
        av.crear_aviso(conn, "las-pintas", "Otra escuela")
        assert a["grupo"] == "3A" and a["texto"] == "Recreo adentro hoy" and a["enviado"] is None
        assert b["grupo"] is None
        assert [x["id"] for x in av.pendientes(conn, "miravalle")] == [a["id"], b["id"]]
        hecho = av.marcar_enviado(conn, a["id"], 12)
        assert hecho["familias"] == 12 and hecho["enviado"] is not None
        primera = hecho["enviado"]
        assert av.marcar_enviado(conn, a["id"], 13)["enviado"] == primera  # idempotente
        assert [x["id"] for x in av.pendientes(conn, "miravalle")] == [b["id"]]
        assert av.marcar_enviado(conn, 999, 1) is None
        assert av.historial(conn, "miravalle")[0]["id"] == b["id"]


def test_suscripciones_sin_datos_personales():
    with db.conexion() as conn:
        s = av.guardar_suscripcion(conn, 12345, "miravalle", ["3a", "5A", "3A", ""])
        assert s == {"chat_id": "12345", "escuela_id": "miravalle", "grupos": ["3A", "5A"]}
        av.guardar_suscripcion(conn, "999", "miravalle", ["1A"])
        assert [x["chat_id"] for x in av.suscripciones(conn, "miravalle", "3A")] == ["12345"]
        assert len(av.suscripciones(conn, "miravalle")) == 2
        assert av.borrar_suscripcion(conn, "12345") and not av.borrar_suscripcion(conn, "12345")
        columnas = {c[1] for c in conn.execute("PRAGMA table_info(suscripciones)").fetchall()}
        assert columnas == {"chat_id", "escuela_id", "grupos", "actualizado"}


def test_reportes_sintomas_solo_conteo():
    with db.conexion() as conn:
        av.reportar_sintomas(conn, "miravalle", "3A")
        av.reportar_sintomas(conn, "miravalle", "3A")
        assert av.reportar_sintomas(conn, "miravalle") == 3
        c = av.conteo_sintomas(conn, "miravalle")
        assert c["total"] == 3 and c["por_grupo"] == {"3A": 2, "sin grupo": 1}


def test_programacion():
    with db.conexion() as conn:
        assert av.leer_programacion(conn, "miravalle", "07:00")["hora"] == "07:00"
        assert av.guardar_programacion(conn, "miravalle", "06:45", "hola")["hora"] == "06:45"
        assert av.leer_programacion(conn, "miravalle", "07:00") == {"escuela_id": "miravalle", "hora": "06:45",
                                                                    "mensaje": "hola"}
        for mala in ("7:00", "24:00", "07:60", "siete"):
            with pytest.raises(ValueError):
                av.guardar_programacion(conn, "miravalle", mala)


def _demo(conn, fuera=62, dentro=19):
    esc.upsert_escuela(conn, "miravalle", "Esc. Prim. Miravalle T/M", "Esc. Prim. Miravalle", "SIMAJ Miravalle")
    db.upsert_salon(conn, "3A", "miravalle", 4, True, "3° A")
    for m in range(0, 60, 10):
        t = AHORA - timedelta(minutes=m)
        db.insertar_lectura(conn, nodo_id="esc-miravalle-fuera", escuela="miravalle", salon_id=None,
                            ubicacion="fuera", pm25=fuera, ts=t)
        db.insertar_lectura(conn, nodo_id="esc-miravalle-salon-3A-dentro", escuela="miravalle", salon_id="3A",
                            ubicacion="dentro", pm25=dentro, ts=t)


def test_info_escuela():
    with db.conexion() as conn:
        _demo(conn)
        e = esc.info_escuela(conn, get_settings(), "miravalle", AHORA)
        assert e["nombreCorto"] == "Esc. Prim. Miravalle" and e["estacion"] == "SIMAJ Miravalle"
        assert e["pm25Hoy"] == 62 and e["semaforoHoy"] == "amarillo" and e["fuente"] == "sensor de afuera"
        assert e["momento"] == "viernes 10:00" and e["actualizado"] == "10:00"
        assert esc.info_escuela(conn, get_settings(), "no-existe", AHORA) is None


def test_escuela_demo_sin_tabla():
    with db.conexion() as conn:
        e = esc.info_escuela(conn, get_settings(), "miravalle", AHORA)
        assert e["nombre"] == "Esc. Prim. Miravalle T/M" and e["pm25Hoy"] is None and e["semaforoHoy"] is None


def test_salon_hoy_y_tareas():
    with db.conexion() as conn:
        _demo(conn)
        salon = db.obtener_salon(conn, "3A")
        m = esc.salon_hoy(conn, get_settings(), salon, AHORA)
        assert m["titulo"] == "Maestra 3° A" and m["salonId"] == "3A" and m["conAsma"] == 4
        assert m["pm25"] == 62 and m["semaforo"] == "amarillo" and m["proteccion"] == 69
        assert [t["id"] for t in m["tareas"]] == ["recreo", "filtro", "inhalador"]
        assert not any(t["hecho"] for t in m["tareas"])
        dia = AHORA.date().isoformat()
        assert esc.alternar_tarea(conn, "3A", "recreo", dia) is True
        assert esc.alternar_tarea(conn, "3A", "recreo", dia) is False
        esc.alternar_tarea(conn, "3A", "filtro", dia, hecho=True)
        t = {x["id"]: x["hecho"] for x in esc.salon_hoy(conn, get_settings(), salon, AHORA)["tareas"]}
        assert t == {"recreo": False, "filtro": True, "inhalador": False}
        with pytest.raises(KeyError):
            esc.alternar_tarea(conn, "3A", "borrar-todo", dia)


def test_tareas_por_semaforo():
    with db.conexion() as conn:
        _demo(conn, fuera=20, dentro=8)
        m = esc.salon_hoy(conn, get_settings(), db.obtener_salon(conn, "3A"), AHORA)
        assert m["semaforo"] == "verde" and "recreo" not in [t["id"] for t in m["tareas"]]


def test_familias_y_mensaje_sin_pronostico():
    with db.conexion() as conn:
        _demo(conn)
        assert esc.familias_a_avisar(conn, "miravalle") == (4, "alumnos con asma (aún sin suscripciones al bot)")
        av.guardar_suscripcion(conn, "1", "miravalle", ["3A"])
        assert esc.familias_a_avisar(conn, "miravalle")[0] == 1
        # sin serie del SIMAJ y fuera de horario escolar no hay pronóstico: mensaje genérico sin números
        texto = esc.mensaje_predeterminado(conn, get_settings(), "miravalle")
        assert "inhalador" in texto and "µg/m³" not in texto


def test_pronostico_marca_sensor_simulado(monkeypatch):
    from app.core import pronostico as pr

    hoy = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    monkeypatch.setattr(db, "ahora", lambda: hoy)
    with db.conexion() as conn:
        db.insertar_lectura(conn, nodo_id="esc-miravalle-fuera", escuela="miravalle", salon_id=None,
                            ubicacion="fuera", pm25=50, ts=hoy, simulada=True)
        assert pr.pronostico_actual(conn, get_settings())["simulado"] is True
        db.insertar_lectura(conn, nodo_id="esc-miravalle-fuera", escuela="miravalle", salon_id=None,
                            ubicacion="fuera", pm25=50, ts=hoy)
        assert pr.pronostico_actual(conn, get_settings())["simulado"] is False

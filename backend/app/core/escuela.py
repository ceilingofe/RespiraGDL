"""Lo que muestran las pantallas de Carlos: datos de la escuela, vista de la maestra y pronóstico de
mañana. Las formas siguen MOCK_ESCUELA, MOCK_MAESTRA y MOCK_PRONOSTICO de frontend/src/data/demo.js."""
from __future__ import annotations

from datetime import datetime, timedelta

from app import db
from app.config import Settings
from app.core.estado import estado_salon
from app.core.pronostico import pronostico_actual
from app.core.semaforo import nivel

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# Escuela de la demo; scripts/cargar_demo.py la guarda en la tabla `escuelas`.
ESCUELAS_DEMO = {
    "miravalle": {"nombre": "Esc. Prim. Miravalle T/M", "nombre_corto": "Esc. Prim. Miravalle",
                  "estacion": "SIMAJ Miravalle"},
}

# Checklist de la maestra según el semáforo. Borrador: lo valida Damaris con el plan de asma.
TAREAS = {
    "verde": [("filtro", "Filtro encendido en horario de clases"),
              ("inhalador", "Recordar inhaladores en la mochila")],
    "amarillo": [("recreo", "Recreo adentro"),
                 ("filtro", "Filtro encendido y puerta cerrada"),
                 ("inhalador", "Preguntar quién trae inhalador")],
    "rojo": [("recreo", "Recreo y educación física adentro"),
             ("filtro", "Filtro encendido, puerta y ventanas cerradas"),
             ("inhalador", "Preguntar quién trae inhalador")],
}
TAREAS_VALIDAS = {tid for lista in TAREAS.values() for tid, _ in lista}


def momento_texto(dt: datetime) -> str:
    return f"{DIAS[dt.weekday()]} {dt:%H:%M}"


def upsert_escuela(conn, escuela_id: str, nombre: str, nombre_corto: str | None, estacion: str | None) -> None:
    conn.execute(
        """INSERT INTO escuelas (id, nombre, nombre_corto, estacion) VALUES (?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET nombre=excluded.nombre, nombre_corto=excluded.nombre_corto,
               estacion=excluded.estacion""",
        (escuela_id.lower(), nombre, nombre_corto, estacion),
    )


def datos_escuela(conn, escuela_id: str) -> dict | None:
    eid = escuela_id.strip().lower()
    f = conn.execute("SELECT * FROM escuelas WHERE id = ?", (eid,)).fetchone()
    if f:
        return {"nombre": f["nombre"], "nombre_corto": f["nombre_corto"] or f["nombre"], "estacion": f["estacion"]}
    if eid in ESCUELAS_DEMO:
        return dict(ESCUELAS_DEMO[eid])
    if conn.execute("SELECT 1 FROM salones WHERE escuela = ? LIMIT 1", (eid,)).fetchone():
        nombre = f"Escuela {eid.replace('-', ' ').title()}"
        return {"nombre": nombre, "nombre_corto": nombre, "estacion": None}
    return None


def pm_fuera_escuela(conn, escuela_id: str, cfg: Settings, momento: datetime | None = None) -> tuple[float | None, str | None]:
    """Promedio de todos los sensores de afuera de la escuela en la última ventana, y la hora de la última lectura."""
    hasta = momento or db.ahora()
    desde = hasta - timedelta(minutes=cfg.ventana_min)
    f = conn.execute(
        """SELECT AVG(pm25) AS p, MAX(ts) AS ultima FROM lecturas
           WHERE escuela = ? AND ubicacion = 'fuera' AND ts BETWEEN ? AND ?""",
        (escuela_id.strip().lower(), desde.isoformat(), hasta.isoformat()),
    ).fetchone()
    return (None if f["p"] is None else float(f["p"])), f["ultima"]


def _pm_y_fuente(conn, escuela_id: str, cfg: Settings, momento: datetime) -> tuple[float | None, str, str | None]:
    pm, ultima = pm_fuera_escuela(conn, escuela_id, cfg, momento)
    if pm is not None:
        return pm, "sensor de afuera", (ultima[11:16] if ultima else None)
    p = pronostico_actual(conn, cfg)
    if p and not p.get("desactualizado"):
        return p["dias"][0]["pm"], f"estación {p.get('estacion') or 'SIMAJ'} ({p['fuente']})", None
    return None, "sin dato", None


def info_escuela(conn, cfg: Settings, escuela_id: str, momento: datetime | None = None) -> dict | None:
    """Forma de MOCK_ESCUELA."""
    datos = datos_escuela(conn, escuela_id)
    if datos is None:
        return None
    ahora = momento or db.ahora()
    pm, fuente, actualizado = _pm_y_fuente(conn, escuela_id, cfg, ahora)
    n = nivel(pm) or {}
    return {
        "id": escuela_id.strip().lower(),
        "nombre": datos["nombre"],
        "nombreCorto": datos["nombre_corto"],
        "estacion": datos["estacion"],
        "semaforoHoy": n.get("semaforo"),
        "nivelHoy": n.get("id"),
        "pm25Hoy": None if pm is None else int(round(pm)),
        "recomendacionHoy": n.get("consejo"),
        "actualizado": actualizado or f"{ahora:%H:%M}",
        "momento": momento_texto(ahora),
        "fuente": fuente,
    }


# ----------------------------------------------------------------------------- vista de la maestra

def tareas_del_dia(conn, salon_id: str, semaforo: str | None, dia: str) -> list[dict]:
    hechas = {f["tarea_id"] for f in conn.execute(
        "SELECT tarea_id FROM tareas_salon WHERE salon_id = ? AND fecha = ? AND hecho = 1", (salon_id, dia)
    ).fetchall()}
    return [{"id": tid, "texto": texto, "hecho": tid in hechas} for tid, texto in TAREAS[semaforo or "verde"]]


def alternar_tarea(conn, salon_id: str, tarea_id: str, dia: str, hecho: bool | None = None) -> bool:
    if tarea_id not in TAREAS_VALIDAS:
        raise KeyError(tarea_id)
    f = conn.execute("SELECT hecho FROM tareas_salon WHERE salon_id = ? AND fecha = ? AND tarea_id = ?",
                     (salon_id, dia, tarea_id)).fetchone()
    nuevo = (not bool(f["hecho"]) if f else True) if hecho is None else bool(hecho)
    conn.execute(
        """INSERT INTO tareas_salon (salon_id, fecha, tarea_id, hecho) VALUES (?, ?, ?, ?)
           ON CONFLICT(salon_id, fecha, tarea_id) DO UPDATE SET hecho=excluded.hecho""",
        (salon_id, dia, tarea_id, int(nuevo)),
    )
    return nuevo


def salon_hoy(conn, cfg: Settings, salon, momento: datetime | None = None) -> dict:
    """Forma de MOCK_MAESTRA: titulo, salonId, semaforo, pm25 (afuera), momento, conAsma, tareas."""
    ahora = momento or db.ahora()
    e = estado_salon(conn, salon, cfg, ahora)
    pm = e["fuera"]
    fuente = e["fuente_fuera"]
    if pm is None:
        pm_esc, fuente, _ = _pm_y_fuente(conn, salon["escuela"], cfg, ahora)
        pm = None if pm_esc is None else int(round(pm_esc))
    procedencia = {"simulado": False, "desactualizado": True, "ultima_lectura": None}
    if pm is not None and fuente.startswith("sensor"):
        filtro = ""
        argumentos = [salon["escuela"], (ahora - timedelta(minutes=cfg.ventana_min)).isoformat(), ahora.isoformat()]
        if fuente == "sensor del salón":
            filtro = " AND salon_id = ?"
            argumentos.append(salon["id"])
        elif fuente == "sensor de la escuela":
            filtro = " AND salon_id IS NULL"
        f = conn.execute(
            "SELECT MAX(ts) AS ultima, MAX(simulada) AS simulada FROM lecturas "
            "WHERE escuela = ? AND ubicacion = 'fuera' AND ts BETWEEN ? AND ?" + filtro,
            argumentos,
        ).fetchone()
        ultima = f["ultima"]
        edad = (ahora - datetime.fromisoformat(ultima)).total_seconds() if ultima else -1
        procedencia = {"simulado": bool(f["simulada"]), "ultima_lectura": ultima,
                       "desactualizado": edad < 0 or edad > cfg.minutos_sin_datos * 60}
    elif pm is not None:
        p = pronostico_actual(conn, cfg)
        if p:
            procedencia["simulado"] = bool(p.get("simulado"))
            procedencia["desactualizado"] = (p["fuente"] == "sensor" or bool(p.get("desactualizado"))
                                              or p["fecha_base"] != ahora.date().isoformat())
    if procedencia["desactualizado"]:
        pm = None  # Un color derivado de un dato vencido aparentaría vigencia.
    n = nivel(pm) or {}
    return {
        "titulo": f"Maestra {e['grupo']}",
        "salonId": e["id"],
        "grupo": e["grupo"],
        "escuela": e["escuela"],
        "semaforo": n.get("semaforo"),
        "nivel": n.get("id"),
        "pm25": pm,
        "recomendacion": n.get("consejo"),
        "dentro": e["dentro"],
        "proteccion": e["proteccion"],
        "estadoProteccion": e["estado"],
        "filtro": e["filtro"],
        "momento": momento_texto(ahora),
        "conAsma": e["asma"],
        "tareas": tareas_del_dia(conn, e["id"], n.get("semaforo"), ahora.date().isoformat()),
        "fuente": fuente,
        **procedencia,
    }


# ----------------------------------------------------------------------------- pronóstico de mañana

def familias_a_avisar(conn, escuela_id: str) -> tuple[int, str]:
    eid = escuela_id.strip().lower()
    n = conn.execute("SELECT COUNT(*) AS n FROM suscripciones WHERE escuela_id = ?", (eid,)).fetchone()["n"]
    if n:
        return int(n), "familias suscritas al bot"
    asma = conn.execute("SELECT COALESCE(SUM(alumnos_asma), 0) AS n FROM salones WHERE escuela = ?",
                        (eid,)).fetchone()["n"]
    return int(asma), "alumnos con asma (aún sin suscripciones al bot)"


def pronostico_manana(conn, cfg: Settings, escuela_id: str) -> dict | None:
    """Forma de MOCK_PRONOSTICO: dia, semaforo, pm25, recomendacion, familiasAviso."""
    p = pronostico_actual(conn, cfg)
    if p is None:
        return None
    m = p["dias"][1]
    familias, fuente_familias = familias_a_avisar(conn, escuela_id)
    return {
        "dia": m["dia"],               # "Mañana", o "Día siguiente" si la serie está desactualizada
        "fecha": m["fecha"],
        "semaforo": m["semaforo"],
        "nivel": m["nivel"],
        "nombre": m["nombre"],
        "pm25": m["pm"],
        "recomendacion": m["consejo"],
        "familiasAviso": familias,
        "fuenteFamilias": fuente_familias,
        "fuente": p["fuente"],
        "desactualizado": bool(p.get("desactualizado")),
        "simulado": bool(p.get("simulado")),   # viene de lecturas simuladas: no mandar aviso real
    }


def mensaje_predeterminado(conn, cfg: Settings, escuela_id: str) -> str:
    """Texto sugerido para el aviso a familias. Orienta; no sustituye la indicación médica."""
    datos = datos_escuela(conn, escuela_id) or {}
    zona = (datos.get("estacion") or "").replace("SIMAJ ", "") or "su colonia"
    m = pronostico_manana(conn, cfg, escuela_id)
    if m is None or m["desactualizado"] or m["pm25"] is None:
        return ("Buenos días. Si su hijo o hija tiene asma, revise que lleve su inhalador de rescate y su plan "
                "de acción. Si usa medicamento de control, no lo suspenda.")
    if m["semaforo"] in ("amarillo", "rojo"):
        return (f"Buenos días. Mañana se espera calidad del aire {m['nombre'].upper()} en {zona} "
                f"(PM2.5 ≈ {m['pm25']} µg/m³). Si su hijo o hija tiene asma, revise que lleve su inhalador "
                "de rescate y su plan. La escuela hará el recreo adentro. Si usa medicamento de control, "
                "no lo suspenda.")
    return (f"Buenos días. Mañana se espera calidad del aire {m['nombre'].lower()} en {zona} "
            f"(PM2.5 ≈ {m['pm25']} µg/m³). Recuerde que su hijo o hija lleve su inhalador de rescate.")

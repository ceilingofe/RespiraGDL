"""Estado de cada salón (fuera, dentro, % de protección) y alertas del día.

Todo es independiente de FastAPI para poder probarlo sin servidor.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app import db
from app.config import Settings
from app.core.proteccion import calcular_proteccion
from app.core.semaforo import nivel

HORA_ENTRADA, HORA_SALIDA = 7, 14  # jornada de primaria matutina


def _r(x: float | None) -> int | None:
    return None if x is None else int(round(x))


def promedio_fuera(conn, salon, desde: datetime, hasta: datetime) -> tuple[float | None, str]:
    """Primero el sensor de afuera del salón; si no hay, el de afuera de la escuela."""
    p = db.promedio(conn, escuela=salon["escuela"], salon_id=salon["id"], ubicacion="fuera",
                    desde=desde, hasta=hasta)
    if p is not None:
        return p, "sensor del salón"
    p = db.promedio(conn, escuela=salon["escuela"], salon_id=None, ubicacion="fuera",
                    desde=desde, hasta=hasta)
    return p, ("sensor de la escuela" if p is not None else "sin dato")


def estado_salon(conn, salon, cfg: Settings, momento: datetime | None = None) -> dict:
    hasta = momento or db.ahora()
    desde = hasta - timedelta(minutes=cfg.ventana_min)
    fuera, fuente_fuera = promedio_fuera(conn, salon, desde, hasta)
    dentro = db.promedio(conn, escuela=salon["escuela"], salon_id=salon["id"], ubicacion="dentro",
                         desde=desde, hasta=hasta)
    prot = calcular_proteccion(fuera, dentro, minimo_fuera=cfg.minimo_fuera,
                               proteccion_minima=cfg.proteccion_minima)
    return {
        "id": salon["id"],
        "escuela": salon["escuela"],
        "grupo": salon["grupo"] or salon["id"],
        "asma": salon["alumnos_asma"],
        "filtro": bool(salon["filtro"]),
        "fuera": _r(fuera),
        "dentro": _r(dentro),
        "proteccion": prot["proteccion_pct"],
        "estado": prot["estado"],
        "nivel_dentro": nivel(dentro),
        "fuente_fuera": fuente_fuera,
        "ventana_min": cfg.ventana_min,
    }


def estados(conn, cfg: Settings, escuela: str | None = None, momento: datetime | None = None) -> list[dict]:
    return [estado_salon(conn, s, cfg, momento) for s in db.listar_salones(conn, escuela)]


def serie_dia(conn, salon, fecha: datetime) -> list[dict]:
    """Serie horaria de la jornada, con la forma de SERIE en frontend/src/data/demo.js:
    [{"h": "7:00", "fuera": 48, "dentro": 40}, ...]"""
    inicio = fecha.replace(hour=HORA_ENTRADA, minute=0, second=0, microsecond=0)
    fin = fecha.replace(hour=HORA_SALIDA, minute=59, second=59, microsecond=0)
    dentro = db.serie_horaria(conn, escuela=salon["escuela"], salon_id=salon["id"], ubicacion="dentro",
                              desde=inicio, hasta=fin)
    fuera = db.serie_horaria(conn, escuela=salon["escuela"], salon_id=salon["id"], ubicacion="fuera",
                             desde=inicio, hasta=fin)
    if not fuera:
        fuera = db.serie_horaria(conn, escuela=salon["escuela"], salon_id=None, ubicacion="fuera",
                                 desde=inicio, hasta=fin)
    serie = []
    for h in range(HORA_ENTRADA, HORA_SALIDA + 1):
        clave = inicio.replace(hour=h).isoformat()[:13]
        if clave in fuera or clave in dentro:
            serie.append({"h": f"{h}:00", "fuera": _r(fuera.get(clave)), "dentro": _r(dentro.get(clave))})
    return serie


def alertas(conn, cfg: Settings, pronostico: dict | None = None, momento: datetime | None = None) -> list[dict]:
    """Reglas simples y explicables. Prioridad: urgente > aviso > info."""
    ahora = momento or db.ahora()
    salida: list[dict] = []

    for e in estados(conn, cfg, momento=ahora):
        if e["filtro"] and e["estado"] == "baja":
            salida.append({
                "tipo": "proteccion_baja", "prioridad": "aviso", "salon_id": e["id"],
                "mensaje": f"{e['grupo']}: protección baja ({e['proteccion']} %). "
                           "Revisar que el filtro esté encendido y la puerta cerrada.",
            })
        if e["dentro"] is not None and e["dentro"] > cfg.umbral_pm25:
            salida.append({
                "tipo": "dentro_alto", "prioridad": "urgente" if e["asma"] else "aviso", "salon_id": e["id"],
                "mensaje": f"{e['grupo']}: PM2.5 dentro del salón en {e['dentro']} µg/m³, "
                           f"arriba de {cfg.umbral_pm25:g}. Hay {e['asma']} alumno(s) con asma.",
            })

    limite = ahora - timedelta(minutes=cfg.minutos_sin_datos)
    for n in db.ultima_por_nodo(conn):
        if n["simulada"]:
            continue
        if datetime.fromisoformat(n["ultima"]) < limite:
            salida.append({
                "tipo": "sensor_desconectado", "prioridad": "info", "salon_id": n["salon_id"],
                "mensaje": f"El sensor {n['nodo_id']} no manda datos desde {n['ultima'][11:16]}. "
                           "Revisar corriente y WiFi.",
            })

    if pronostico:
        manana = next((d for d in pronostico.get("dias", []) if d.get("dia") == "Mañana"), None)
        if manana and manana.get("semaforo") in ("amarillo", "rojo"):
            familias = sum(s["alumnos_asma"] for s in db.listar_salones(conn))
            salida.append({
                "tipo": "pronostico", "prioridad": "urgente" if manana["semaforo"] == "rojo" else "aviso",
                "salon_id": None,
                "mensaje": f"Mañana se espera calidad del aire {manana['nombre'].upper()} "
                           f"(PM2.5 ≈ {manana['pm']}). {manana['consejo']} Avisar a {familias} familias "
                           "de alumnos con asma.",
                "familias": familias,
            })

    orden = {"urgente": 0, "aviso": 1, "info": 2}
    return sorted(salida, key=lambda a: orden[a["prioridad"]])

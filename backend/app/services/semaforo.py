"""Semáforo de PM2.5 y protocolo del plan de asma escolar.

Los cortes son los mismos que frontend/src/data/demo.js (NIVELES): si cambian, cambien ambos.
Borrador: el contenido de salud lo valida un médico (issues #13 y #14). Orienta, no diagnostica.
"""

NORMA_PM25 = 45  # µg/m³ promedio 24 h, NOM-025-SSA1-2021

# (id, nombre, color del LED/bot, máximo µg/m³)
NIVELES = [
    ("good", "Buena", "verde", 15),
    ("ok", "Aceptable", "verde", 33),
    ("bad", "Mala", "amarillo", 79),
    ("vbad", "Muy mala", "rojo", 130),
    ("ext", "Extremadamente mala", "rojo", float("inf")),
]

PROTOCOLO = {
    "good": {
        "titulo": "Día normal",
        "escuela": ["Recreo y educación física al aire libre.", "Filtro encendido en horario de clases."],
        "maestro": ["Recreo normal.", "Revisar que el filtro esté encendido al llegar."],
        "familias": [],
    },
    "ok": {
        "titulo": "Día normal con atención",
        "escuela": ["Recreo al aire libre.", "Filtro encendido en horario de clases."],
        "maestro": ["Recreo normal; observar a los alumnos con asma.", "Filtro encendido y puerta cerrada."],
        "familias": ["Recordar el inhalador de rescate en la mochila."],
    },
    "bad": {
        "titulo": "Aire malo: proteger a quienes tienen asma",
        "escuela": [
            "Recreo adentro para alumnos con asma.",
            "Educación física de baja intensidad o adentro.",
            "Enviar aviso a familias a las 7:00.",
        ],
        "maestro": [
            "Recreo adentro para alumnos con asma.",
            "Filtro encendido y puerta cerrada.",
            "Preguntar quién trae su inhalador de rescate.",
        ],
        "familias": ["Que lleve su inhalador de rescate.", "Si usa medicamento de control, no lo suspenda."],
    },
    "vbad": {
        "titulo": "Aire muy malo: recreo adentro para todos",
        "escuela": [
            "Recreo y educación física adentro para todo el grupo.",
            "Ventanas cerradas y filtro al máximo.",
            "Enviar aviso a familias un día antes y a las 7:00.",
        ],
        "maestro": [
            "Recreo adentro para todos.",
            "Ventanas cerradas y filtro al máximo.",
            "Preguntar quién trae su inhalador de rescate.",
            "Tener a la mano la guía de crisis.",
        ],
        "familias": [
            "Que lleve su inhalador de rescate.",
            "Si usa medicamento de control, no lo suspenda.",
            "Evitar ejercicio al aire libre por la tarde.",
        ],
    },
    "ext": {
        "titulo": "Contingencia: seguir a Protección Civil",
        "escuela": ["Seguir indicaciones de Protección Civil y de la SEJ.", "Todas las actividades adentro."],
        "maestro": ["Todas las actividades adentro.", "Ventanas cerradas y filtro al máximo.", "Tener a la mano la guía de crisis."],
        "familias": ["Seguir avisos oficiales.", "Que lleve su inhalador de rescate."],
    },
}


def nivel(pm25: float) -> dict:
    """Nivel del semáforo para un valor de PM2.5 (µg/m³)."""
    if pm25 < 0:
        raise ValueError("PM2.5 no puede ser negativo")
    for id_, nombre, color, maximo in NIVELES:
        if pm25 <= maximo:
            return {"id": id_, "nombre": nombre, "color": color, "pm25": round(pm25)}
    raise AssertionError("inalcanzable")


def protocolo(pm25: float) -> dict:
    """Nivel + qué hacen escuela, maestro y familias ese día."""
    n = nivel(pm25)
    return {**n, **PROTOCOLO[n["id"]]}


def mensaje_familias(pm25_manana: float, zona: str) -> str:
    """Texto del aviso a familias para el bot y el tablero."""
    n = nivel(pm25_manana)
    acciones = PROTOCOLO[n["id"]]["familias"]
    if not acciones:
        return f"Mañana se espera calidad del aire {n['nombre'].upper()} en {zona} (PM2.5 {n['pm25']}). Recreo normal."
    lista = " ".join(acciones)
    return (
        f"Mañana se espera calidad del aire {n['nombre'].upper()} en {zona} (PM2.5 {n['pm25']}). "
        f"Si su hijo o hija tiene asma: {lista}"
    )

"""Aula Limpia: % de protección, semáforo de PM2.5 y recomendaciones para el salón.

Misma lógica que frontend/src/aula/logica.js. Orienta y recuerda; no es herramienta de diagnóstico.
"""
from datetime import date

NORMA_PM25 = 45  # µg/m³ promedio 24 h, NOM-025-SSA1-2021
PROTECCION_MINIMA = 40
DIAS_CAMBIO_FILTRO = 90

# (máximo, id, nombre); cortes iguales a los del tablero
NIVELES = [
    (25, "good", "Buena"),
    (45, "ok", "Aceptable"),
    (79, "bad", "Mala"),
    (147, "vbad", "Muy mala"),
    (float("inf"), "ext", "Extremadamente mala"),
]


def rango(pm: float) -> int:
    return next(i for i, (mx, _, _) in enumerate(NIVELES) if pm <= mx)


def nivel(pm: float) -> dict:
    _, id_, nombre = NIVELES[rango(pm)]
    return {"id": id_, "nombre": nombre}


def proteccion(fuera: float, dentro: float) -> int | None:
    """% de PM2.5 de fuera que no entra al salón = 1 − dentro/fuera."""
    if not fuera or fuera <= 0:
        return None
    return round((1 - dentro / fuera) * 100)


def recomendaciones(fuera: float, dentro: float, filtro: bool = True, asma: int = 0,
                    filtro_cambio: date | None = None, hoy: date | None = None) -> list[dict]:
    r: list[dict] = []
    p = proteccion(fuera, dentro)
    nf, nd = rango(fuera), rango(dentro)

    if not filtro:
        r.append({"prioridad": "alta", "texto": "Enciende el filtro y cierra la puerta.",
                  "porque": "Sin filtro, casi todo el PM2.5 de fuera entra al salón."})
    elif p is not None and p < PROTECCION_MINIMA and nf >= 1:
        r.append({"prioridad": "alta", "texto": "Protección baja: cierra puerta y ventanas y revisa que nada tape el filtro.",
                  "porque": f"Solo se detiene el {max(p, 0)} % del PM2.5 de fuera."})

    if dentro > NORMA_PM25:
        r.append({"prioridad": "alta", "texto": "Dentro del salón se rebasa la norma. Evita actividad física intensa adentro.",
                  "porque": f"PM2.5 dentro {round(dentro)} µg/m³; la norma es {NORMA_PM25}."})

    if nf >= 3:
        r.append({"prioridad": "alta", "texto": "Recreo adentro para todo el grupo.",
                  "porque": f"La calidad del aire de fuera es {nivel(fuera)['nombre'].lower()}."})
    elif nf == 2:
        quien = "el alumno" if asma == 1 else f"los {asma} alumnos"
        texto = f"Recreo adentro para {quien} con asma." if asma > 0 else "Recreo corto o adentro si hay alumnos con asma."
        r.append({"prioridad": "media", "texto": texto, "porque": "La calidad del aire de fuera es mala."})

    if asma > 0 and nf >= 2:
        r.append({"prioridad": "media", "texto": "Recuerda al grupo traer su inhalador en la mochila.",
                  "porque": "Días de aire malo aumentan el riesgo de crisis."})

    if filtro_cambio:
        dias = ((hoy or date.today()) - filtro_cambio).days
        if dias >= DIAS_CAMBIO_FILTRO:
            r.append({"prioridad": "media", "texto": "Toca cambiar los 4 filtros MERV-13.",
                      "porque": f"Llevan {dias} días; se cambian cada {DIAS_CAMBIO_FILTRO}."})

    if nf == 0 and nd <= 1:
        r.append({"prioridad": "ok", "texto": "Aire de fuera bueno: abre ventanas 10 minutos entre clases para ventilar.",
                  "porque": "Ventilar baja el CO₂ y el calor del salón."})
    if not any(x["prioridad"] == "alta" for x in r) and filtro and p is not None and p >= PROTECCION_MINIMA:
        r.append({"prioridad": "ok", "texto": "El filtro está funcionando. Mantén la puerta cerrada.",
                  "porque": f"Se detiene el {p} % del PM2.5 de fuera."})

    orden = {"alta": 0, "media": 1, "ok": 2}
    return sorted(r, key=lambda x: orden[x["prioridad"]])

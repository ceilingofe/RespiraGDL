"""% de PM2.5 que no entra al salón: protección = 1 − dentro / fuera.

Se calcula con promedios de una ventana (por defecto 60 min) de cada sensor, no con
lecturas sueltas, porque el PMS5003 tiene ruido de segundo a segundo.
"""
from __future__ import annotations


def calcular_proteccion(
    fuera: float | None,
    dentro: float | None,
    *,
    minimo_fuera: float = 10.0,
    proteccion_minima: float = 40.0,
) -> dict:
    """Devuelve {"proteccion_pct": int | None, "estado": str}.

    estado:
      sin_datos   falta el promedio de dentro o de fuera
      aire_limpio afuera hay menos de `minimo_fuera` µg/m³: el % no significa nada
      baja        protección menor que `proteccion_minima`
      ok          protección aceptable
    """
    if fuera is None or dentro is None:
        return {"proteccion_pct": None, "estado": "sin_datos"}
    if fuera < minimo_fuera:
        return {"proteccion_pct": None, "estado": "aire_limpio"}
    pct = (1.0 - dentro / fuera) * 100.0
    pct = max(0.0, min(100.0, pct))  # si dentro > fuera (p. ej. polvo de gis) se reporta 0 %
    pct_int = int(round(pct))
    return {"proteccion_pct": pct_int, "estado": "baja" if pct < proteccion_minima else "ok"}

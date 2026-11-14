from datetime import date

from fastapi import APIRouter, Query

from app.services import aula

router = APIRouter(prefix="/aula", tags=["aula limpia"])


@router.get("/estado")
def estado(
    fuera: float = Query(..., ge=0, description="PM2.5 fuera del salón (µg/m³)"),
    dentro: float = Query(..., ge=0, description="PM2.5 dentro del salón (µg/m³)"),
    filtro: bool = True,
    asma: int = Query(0, ge=0, description="Número de alumnos con asma (sin nombres)"),
    filtro_cambio: date | None = None,
):
    """Semáforo, % de protección y recomendaciones para un salón.

    Lo usan la página Aula Limpia, el bot y el LED del nodo. Cuando /lecturas guarde datos,
    /salones/{id}/proteccion puede llamar a esta misma lógica con el promedio de la última hora.
    """
    return {
        "fuera": {"pm25": fuera, **aula.nivel(fuera)},
        "dentro": {"pm25": dentro, **aula.nivel(dentro)},
        "proteccion_pct": aula.proteccion(fuera, dentro),
        "recomendaciones": aula.recomendaciones(fuera, dentro, filtro, asma, filtro_cambio),
    }

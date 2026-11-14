"""Configuración leída del entorno (.env). Se lee en cada llamada para que las pruebas
puedan cambiarla con monkeypatch."""
import os
from dataclasses import dataclass
from pathlib import Path

try:  # python-dotenv está en requirements; si falta, se usan las variables del sistema
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    db_path: str
    umbral_pm25: float          # norma de referencia para la línea del tablero y la alerta "dentro alto"
    nodo_token: str             # si está vacío, los nodos no mandan token (demo)
    ventana_min: int            # minutos que se promedian para el % de protección
    proteccion_minima: float    # % debajo del cual se alerta "revisar filtro"
    minutos_sin_datos: int      # un nodo sin datos por más de esto se marca desconectado
    minimo_fuera: float         # si afuera hay menos PM2.5, no se calcula % (aire limpio)
    modelo_path: Path
    serie_simaj: Path
    estacion_referencia: str


def _db_path(url: str) -> str:
    prefijo = "sqlite:///"
    if not url.startswith(prefijo):
        raise ValueError("Por ahora solo se soporta SQLite: DATABASE_URL=sqlite:///./respira.sqlite3")
    return url[len(prefijo):]


def get_settings() -> Settings:
    return Settings(
        db_path=_db_path(os.getenv("DATABASE_URL", "sqlite:///./respira.sqlite3")),
        umbral_pm25=float(os.getenv("ALERTA_UMBRAL_PM25", "25")),
        nodo_token=os.getenv("NODO_TOKEN", ""),
        ventana_min=int(os.getenv("VENTANA_PROTECCION_MIN", "60")),
        proteccion_minima=float(os.getenv("PROTECCION_MINIMA", "40")),
        minutos_sin_datos=int(os.getenv("MINUTOS_SIN_DATOS", "10")),
        minimo_fuera=float(os.getenv("MINIMO_PM25_FUERA", "10")),
        modelo_path=Path(os.getenv("MODELO_PATH", str(REPO_ROOT / "ml" / "modelos" / "pronostico_pm25.joblib"))),
        serie_simaj=Path(os.getenv("SERIE_SIMAJ", str(REPO_ROOT / "data" / "processed" / "simaj_horario.csv"))),
        estacion_referencia=os.getenv("ESTACION_REFERENCIA", "Miravalle"),
    )

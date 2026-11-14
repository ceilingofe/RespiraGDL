import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def base_temporal(tmp_path, monkeypatch):
    """Cada prueba usa su propia base SQLite y no lee modelo ni serie del SIMAJ reales."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'prueba.sqlite3'}")
    monkeypatch.setenv("MODELO_PATH", str(tmp_path / "no-existe.joblib"))
    monkeypatch.setenv("SERIE_SIMAJ", str(tmp_path / "no-existe.csv"))
    monkeypatch.delenv("NODO_TOKEN", raising=False)
    yield tmp_path

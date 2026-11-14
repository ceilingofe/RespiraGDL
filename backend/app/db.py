"""Base de datos SQLite (demo). Usa solo la librería estándar para que corra en cualquier laptop.

Tablas:
  salones  conteo de alumnos con asma por grupo (SIN nombres) y si tiene filtro
  lecturas PM2.5 de cada nodo con la hora del servidor; `simulada` marca datos que no
           vienen de un sensor real (regla 5 del kit: decir qué parte está simulada)
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from app.config import get_settings

ESQUEMA = """
CREATE TABLE IF NOT EXISTS salones (
    id            TEXT PRIMARY KEY,          -- p. ej. 3B
    escuela       TEXT NOT NULL,             -- p. ej. miravalle (igual que en el nodo_id)
    grupo         TEXT,                      -- texto para mostrar: 3° B
    alumnos_asma  INTEGER NOT NULL DEFAULT 0 CHECK (alumnos_asma >= 0),
    filtro        INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS lecturas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nodo_id    TEXT NOT NULL,
    escuela    TEXT NOT NULL,
    salon_id   TEXT,                         -- NULL = sensor de afuera de la escuela
    ubicacion  TEXT NOT NULL CHECK (ubicacion IN ('dentro', 'fuera')),
    pm25       REAL NOT NULL,
    pm10       REAL,
    ts         TEXT NOT NULL,                -- hora local del servidor, ISO 8601
    simulada   INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_lect_salon ON lecturas (escuela, salon_id, ubicacion, ts);
CREATE INDEX IF NOT EXISTS ix_lect_nodo ON lecturas (nodo_id, ts);
"""


def _conectar(path: str) -> sqlite3.Connection:
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode=WAL")  # el ESP32 escribe mientras el tablero lee
    conn.executescript(ESQUEMA)  # idempotente: la base se crea sola la primera vez
    return conn


def init_db(path: str | None = None) -> None:
    with conexion(path) as conn:
        conn.executescript(ESQUEMA)


@contextmanager
def conexion(path: str | None = None) -> Iterator[sqlite3.Connection]:
    """Una conexión por petición; hace commit al salir sin error."""
    conn = _conectar(path or get_settings().db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ahora() -> datetime:
    return datetime.now().replace(microsecond=0)


# ----------------------------------------------------------------------------- salones

def upsert_salon(conn, salon_id: str, escuela: str, alumnos_asma: int, filtro: bool = True,
                 grupo: str | None = None) -> None:
    conn.execute(
        """INSERT INTO salones (id, escuela, grupo, alumnos_asma, filtro) VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET escuela=excluded.escuela, grupo=excluded.grupo,
               alumnos_asma=excluded.alumnos_asma, filtro=excluded.filtro""",
        (salon_id.upper(), escuela, grupo, int(alumnos_asma), int(bool(filtro))),
    )


def listar_salones(conn, escuela: str | None = None) -> list[sqlite3.Row]:
    if escuela:
        return conn.execute("SELECT * FROM salones WHERE escuela=? ORDER BY id", (escuela,)).fetchall()
    return conn.execute("SELECT * FROM salones ORDER BY escuela, id").fetchall()


def obtener_salon(conn, salon_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM salones WHERE id=?", (salon_id.upper(),)).fetchone()


# ----------------------------------------------------------------------------- lecturas

def insertar_lectura(conn, *, nodo_id: str, escuela: str, salon_id: str | None, ubicacion: str,
                     pm25: float, pm10: float | None = None, ts: datetime | None = None,
                     simulada: bool = False) -> int:
    cur = conn.execute(
        """INSERT INTO lecturas (nodo_id, escuela, salon_id, ubicacion, pm25, pm10, ts, simulada)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (nodo_id, escuela, salon_id, ubicacion, float(pm25), pm10, (ts or ahora()).replace(microsecond=0).isoformat(),
         int(simulada)),
    )
    return int(cur.lastrowid)


def promedio(conn, *, escuela: str, salon_id: str | None, ubicacion: str, desde: datetime,
             hasta: datetime) -> float | None:
    """Promedio de PM2.5 en [desde, hasta]. salon_id=None busca el sensor de afuera de la escuela."""
    if salon_id is None:
        filtro_salon, args = "salon_id IS NULL", ()
    else:
        filtro_salon, args = "salon_id = ?", (salon_id,)
    fila = conn.execute(
        f"""SELECT AVG(pm25) AS p FROM lecturas
            WHERE escuela=? AND {filtro_salon} AND ubicacion=? AND ts BETWEEN ? AND ?""",
        (escuela, *args, ubicacion, desde.isoformat(), hasta.isoformat()),
    ).fetchone()
    return None if fila["p"] is None else float(fila["p"])


def lecturas_recientes(conn, *, salon_id: str | None = None, desde: datetime | None = None,
                       limite: int = 500) -> list[sqlite3.Row]:
    sql, args = "SELECT * FROM lecturas WHERE 1=1", []
    if salon_id:
        sql += " AND salon_id = ?"
        args.append(salon_id.upper())
    if desde:
        sql += " AND ts >= ?"
        args.append(desde.isoformat())
    sql += " ORDER BY ts DESC LIMIT ?"
    args.append(int(limite))
    return conn.execute(sql, args).fetchall()


def ultima_por_nodo(conn) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT nodo_id, escuela, salon_id, ubicacion, MAX(ts) AS ultima, MAX(simulada) AS simulada
           FROM lecturas GROUP BY nodo_id ORDER BY nodo_id"""
    ).fetchall()


def serie_horaria(conn, *, escuela: str, salon_id: str | None, ubicacion: str, desde: datetime,
                  hasta: datetime) -> dict[str, float]:
    """Promedio por hora: {"2026-11-14T10": 21.4, ...}"""
    if salon_id is None:
        filtro_salon, args = "salon_id IS NULL", ()
    else:
        filtro_salon, args = "salon_id = ?", (salon_id,)
    filas = conn.execute(
        f"""SELECT substr(ts, 1, 13) AS hora, AVG(pm25) AS p FROM lecturas
            WHERE escuela=? AND {filtro_salon} AND ubicacion=? AND ts BETWEEN ? AND ?
            GROUP BY hora ORDER BY hora""",
        (escuela, *args, ubicacion, desde.isoformat(), hasta.isoformat()),
    ).fetchall()
    return {f["hora"]: float(f["p"]) for f in filas}

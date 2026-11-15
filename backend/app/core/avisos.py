"""Avisos a familias, suscripciones del bot, reportes de síntomas y hora del aviso diario.

Flujo de un aviso (contrato del bot de Carlos, bot/bot.py):
    tablero o maestra  -> POST /alertas/aviso            (queda pendiente)
    bot, cada 30 s     -> GET  /alertas/aviso/pendientes (lo reparte por grupo)
    bot                -> POST /alertas/aviso/{id}/enviado {"familias": n}

Privacidad: nunca se guardan nombres ni teléfonos. De Telegram solo el chat_id y los grupos;
de los reportes de síntomas, solo el conteo por día y grupo.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime

from app import db

_HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _grupo(g: str | None) -> str | None:
    g = (g or "").strip().upper()
    return g or None


def _fila_aviso(f) -> dict:
    return {"id": f["id"], "escuela_id": f["escuela_id"], "grupo": f["grupo"], "texto": f["texto"],
            "origen": f["origen"], "creado": f["creado"], "enviado": f["enviado"], "familias": f["familias"]}


# ----------------------------------------------------------------------------- avisos

def crear_aviso(conn, escuela_id: str, texto: str, grupo: str | None = None, origen: str = "tablero",
                momento: datetime | None = None) -> dict:
    cur = conn.execute(
        "INSERT INTO avisos (escuela_id, grupo, texto, origen, creado) VALUES (?, ?, ?, ?, ?)",
        (escuela_id.strip().lower(), _grupo(grupo), texto.strip(), origen,
         (momento or db.ahora()).isoformat()),
    )
    return obtener_aviso(conn, int(cur.lastrowid))


def obtener_aviso(conn, aviso_id: int) -> dict | None:
    f = conn.execute("SELECT * FROM avisos WHERE id = ?", (aviso_id,)).fetchone()
    return _fila_aviso(f) if f else None


def pendientes(conn, escuela_id: str | None = None) -> list[dict]:
    sql, args = "SELECT * FROM avisos WHERE enviado IS NULL", []
    if escuela_id:
        sql += " AND escuela_id = ?"
        args.append(escuela_id.strip().lower())
    return [_fila_aviso(f) for f in conn.execute(sql + " ORDER BY id", args).fetchall()]


def historial(conn, escuela_id: str | None = None, limite: int = 20) -> list[dict]:
    sql, args = "SELECT * FROM avisos", []
    if escuela_id:
        sql += " WHERE escuela_id = ?"
        args.append(escuela_id.strip().lower())
    sql += " ORDER BY id DESC LIMIT ?"
    args.append(int(limite))
    return [_fila_aviso(f) for f in conn.execute(sql, args).fetchall()]


def marcar_enviado(conn, aviso_id: int, familias: int, momento: datetime | None = None) -> dict | None:
    """Idempotente: si ya estaba enviado, solo actualiza el número de familias."""
    conn.execute(
        "UPDATE avisos SET enviado = COALESCE(enviado, ?), familias = ? WHERE id = ?",
        ((momento or db.ahora()).isoformat(), int(familias), aviso_id),
    )
    return obtener_aviso(conn, aviso_id)


# ----------------------------------------------------------------------------- suscripciones

def guardar_suscripcion(conn, chat_id: str, escuela_id: str, grupos: list[str]) -> dict:
    limpios = sorted({g for g in (_grupo(x) for x in grupos) if g})
    conn.execute(
        """INSERT INTO suscripciones (chat_id, escuela_id, grupos, actualizado) VALUES (?, ?, ?, ?)
           ON CONFLICT(chat_id) DO UPDATE SET escuela_id=excluded.escuela_id, grupos=excluded.grupos,
               actualizado=excluded.actualizado""",
        (str(chat_id), escuela_id.strip().lower(), json.dumps(limpios), db.ahora().isoformat()),
    )
    return {"chat_id": str(chat_id), "escuela_id": escuela_id.strip().lower(), "grupos": limpios}


def borrar_suscripcion(conn, chat_id: str) -> bool:
    return conn.execute("DELETE FROM suscripciones WHERE chat_id = ?", (str(chat_id),)).rowcount > 0


def suscripciones(conn, escuela_id: str | None = None, grupo: str | None = None) -> list[dict]:
    sql, args = "SELECT * FROM suscripciones", []
    if escuela_id:
        sql += " WHERE escuela_id = ?"
        args.append(escuela_id.strip().lower())
    salida = []
    for f in conn.execute(sql + " ORDER BY chat_id", args).fetchall():
        grupos = json.loads(f["grupos"])
        if grupo and _grupo(grupo) not in grupos:
            continue
        salida.append({"chat_id": f["chat_id"], "escuela_id": f["escuela_id"], "grupos": grupos})
    return salida


# ----------------------------------------------------------------------------- reportes de síntomas

def reportar_sintomas(conn, escuela_id: str, grupo: str | None = None, dia: date | None = None) -> int:
    dia = dia or db.ahora().date()
    conn.execute("INSERT INTO reportes_sintomas (escuela_id, grupo, fecha) VALUES (?, ?, ?)",
                 (escuela_id.strip().lower(), _grupo(grupo), dia.isoformat()))
    return conteo_sintomas(conn, escuela_id, dia)["total"]


def conteo_sintomas(conn, escuela_id: str, dia: date | None = None) -> dict:
    dia = dia or db.ahora().date()
    filas = conn.execute(
        """SELECT COALESCE(grupo, 'sin grupo') AS g, COUNT(*) AS n FROM reportes_sintomas
           WHERE escuela_id = ? AND fecha = ? GROUP BY g ORDER BY g""",
        (escuela_id.strip().lower(), dia.isoformat()),
    ).fetchall()
    por_grupo = {f["g"]: f["n"] for f in filas}
    return {"escuela_id": escuela_id.strip().lower(), "fecha": dia.isoformat(),
            "total": sum(por_grupo.values()), "por_grupo": por_grupo}


# ----------------------------------------------------------------------------- programación

def validar_hora(hora: str) -> str:
    if not _HORA.match(hora.strip()):
        raise ValueError("hora debe ser HH:MM en 24 h, p. ej. 07:00")
    return hora.strip()


def leer_programacion(conn, escuela_id: str, hora_default: str) -> dict:
    f = conn.execute("SELECT * FROM programacion WHERE escuela_id = ?", (escuela_id.strip().lower(),)).fetchone()
    if f is None:
        return {"escuela_id": escuela_id.strip().lower(), "hora": hora_default, "mensaje": None}
    return {"escuela_id": f["escuela_id"], "hora": f["hora"], "mensaje": f["mensaje"]}


def guardar_programacion(conn, escuela_id: str, hora: str, mensaje: str | None = None) -> dict:
    conn.execute(
        """INSERT INTO programacion (escuela_id, hora, mensaje) VALUES (?, ?, ?)
           ON CONFLICT(escuela_id) DO UPDATE SET hora=excluded.hora, mensaje=excluded.mensaje""",
        (escuela_id.strip().lower(), validar_hora(hora), mensaje),
    )
    return leer_programacion(conn, escuela_id, hora)

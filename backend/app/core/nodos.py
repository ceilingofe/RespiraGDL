"""Convención de nombres de los nodos ESP32 (ver firmware/nodo-aire/include/config.example.h).

    esc-<escuela>-salon-<salon>-<dentro|fuera>   sensor de un salón
    esc-<escuela>-fuera                          sensor de afuera compartido por la escuela

Ejemplos: esc-miravalle-salon-3B-dentro, esc-miravalle-salon-3B-fuera, esc-miravalle-fuera
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_SALON = re.compile(r"^esc-(?P<escuela>[a-z0-9_]+(?:-[a-z0-9_]+)*?)-salon-(?P<salon>[A-Za-z0-9]+)-(?P<ubic>dentro|fuera)$", re.I)
_ESCUELA = re.compile(r"^esc-(?P<escuela>[a-z0-9_]+(?:-[a-z0-9_]+)*?)-(?P<ubic>fuera)$", re.I)


@dataclass(frozen=True)
class Nodo:
    escuela: str
    salon_id: str | None   # None = sensor de afuera de toda la escuela
    ubicacion: str          # "dentro" | "fuera"


def parse_nodo_id(nodo_id: str) -> Nodo:
    nid = nodo_id.strip()
    m = _SALON.match(nid)
    if m:
        return Nodo(m["escuela"].lower(), m["salon"].upper(), m["ubic"].lower())
    m = _ESCUELA.match(nid)
    if m:
        return Nodo(m["escuela"].lower(), None, "fuera")
    raise ValueError(
        f"nodo_id '{nodo_id}' no sigue la convención esc-<escuela>-salon-<salon>-<dentro|fuera> "
        "o esc-<escuela>-fuera"
    )

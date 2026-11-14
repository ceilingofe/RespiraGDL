"""Descarga de datos de estaciones del SIMAJ vía SINAICA (dataset 39 del kit).

Usa el mismo servicio que la página pública https://sinaica.inecc.gob.mx/data.php
(documentado por el paquete de R `rsinaica`, MIT, de Diego Valle-Jones):

    POST https://sinaica.inecc.gob.mx/pags/datGrafs.php
         estacionId=<id>&param=<PM2.5>&fechaIni=<YYYY-MM-DD>&rango=<1|2|3|4>&tipoDatos=<"" | V | M>
    rango: 1 = 1 día, 2 = 1 semana, 3 = 2 semanas, 4 = 1 mes
    La respuesta es HTML con un arreglo JavaScript `var dat = [...]`.

Solo usa la librería estándar. No es una API oficial: si SINAICA cambia la página,
descargar a mano desde data.php (o aire.jalisco.gob.mx) y guardar el CSV en data/raw/
con las columnas estacion,parametro,fecha,hora,valor.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date

BASE_URL = "https://sinaica.inecc.gob.mx"
URL_DATOS = f"{BASE_URL}/pags/datGrafs.php"
URL_PAGINA = f"{BASE_URL}/data.php"
USER_AGENT = "RespiraGDL-Hackathon-Jalisco-2026 (proyecto escolar)"

# IDs de SINAICA de la red Guadalajara (SIMAJ), confirmados contra el catálogo
# stations_sinaica del paquete rsinaica el 2026-11-14. Ojo: el 103 es Las Águilas,
# no Las Pintas. Otras estaciones se ubican con: python data/scripts/descargar_sinaica.py --buscar
ESTACIONES_CONOCIDAS = {"Centro": 102, "Miravalle": 106, "Las Pintas": 104, "Santa Fe": 108}

# Parámetros útiles para el modelo. TMPI = temperatura en la estación Centro;
# otras estaciones pueden usar TMP. Si un parámetro no existe, la descarga regresa vacío.
PARAMETROS = ("PM2.5", "PM10", "TMPI", "TMP", "HR", "VV")

TIPOS = {"crudos": "", "validados": "V", "manuales": "M"}

_RE_DAT = re.compile(r"var\s+dat\s*=\s*(\[.*?\]);", re.S)
_RE_OPCION = re.compile(r"<option[^>]*value=['\"]?(\d+)['\"]?[^>]*>([^<]+)</option>", re.I)


def _post(url: str, campos: dict, timeout: int = 60) -> str:
    datos = urllib.parse.urlencode(campos).encode()
    req = urllib.request.Request(url, data=datos, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def parsear_respuesta(html: str) -> list[dict]:
    """Extrae `var dat = [...]` y normaliza los nombres de campo.

    rsinaica renombra los campos a id, date, hour, value, valid (y descarta bandO);
    aquí se aceptan nombres en español o inglés para no depender del orden.
    """
    m = _RE_DAT.search(html)
    if not m:
        return []
    crudos = json.loads(m.group(1))
    filas = []
    for c in crudos:
        if isinstance(c, dict):
            k = {key.lower(): v for key, v in c.items()}
            fecha = k.get("fecha") or k.get("date")
            hora = k.get("hora", k.get("hour"))
            valor = k.get("valor", k.get("value"))
            valido = k.get("val", k.get("valid", k.get("validoorig")))
        else:  # lista: [id, fecha, hora, valor, bandO, val]
            fecha, hora, valor = c[1], c[2], c[3]
            valido = c[5] if len(c) > 5 else None
        if fecha is None or hora is None:
            continue
        filas.append({"fecha": str(fecha)[:10], "hora": int(hora),
                      "valor": None if valor in (None, "") else float(valor),
                      "valido": None if valido in (None, "") else int(valido)})
    return filas


def descargar_mes(estacion_id: int, parametro: str, anio: int, mes: int, tipo: str = "crudos") -> list[dict]:
    html = _post(URL_DATOS, {
        "estacionId": estacion_id, "param": parametro,
        "fechaIni": date(anio, mes, 1).isoformat(), "rango": 4, "tipoDatos": TIPOS[tipo],
    })
    filas = parsear_respuesta(html)
    # rango=4 puede traer días del mes siguiente: se recorta al mes pedido
    prefijo = f"{anio:04d}-{mes:02d}"
    return [f for f in filas if f["fecha"].startswith(prefijo)]


def meses(desde: date, hasta: date):
    a, m = desde.year, desde.month
    while (a, m) <= (hasta.year, hasta.month):
        yield a, m
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def descargar_rango(estacion_id: int, parametro: str, desde: date, hasta: date, tipo: str = "crudos",
                    pausa: float = 0.5, log=print) -> list[dict]:
    todas = []
    for a, m in meses(desde, hasta):
        try:
            filas = descargar_mes(estacion_id, parametro, a, m, tipo)
        except Exception as exc:  # un mes que falla no tumba toda la descarga
            log(f"  ! {parametro} {a}-{m:02d}: {exc}")
            filas = []
        log(f"  {parametro} {a}-{m:02d}: {len(filas)} horas")
        todas.extend(filas)
        time.sleep(pausa)  # no saturar el servidor del INECC
    return todas


def listar_estaciones_pagina() -> dict[int, str]:
    """Intenta leer el menú de estaciones de data.php (si la página lo trae en el HTML)."""
    req = urllib.request.Request(URL_PAGINA, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", errors="replace")
    return {int(i): nombre.strip() for i, nombre in _RE_OPCION.findall(html)}

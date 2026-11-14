Los datos crudos no se suben al repo (`data/raw/*` está en `.gitignore`). Cada script en `scripts/` documenta de dónde baja cada archivo.

| Script | Qué hace | Salida |
| --- | --- | --- |
| `scripts/descargar_sinaica.py` | Baja PM2.5, PM10 y clima horarios del SIMAJ vía SINAICA (dataset 39 del kit) | `raw/sinaica_<estación>_<parámetro>_<tipo>.csv` |
| `scripts/procesar_sinaica.py` | Limpia, junta y rellena huecos cortos | `processed/simaj_horario.csv`, `processed/resumen_datos.csv` |

Si la descarga automática falla (SINAICA cambió la página, o no hay red), bajen el CSV a mano desde https://sinaica.inecc.gob.mx/data.php o aire.jalisco.gob.mx. Guárdenlo en `raw/` con nombre `sinaica_*.csv` y estas columnas: `estacion,estacion_id,parametro,fecha,hora,valor,valido`.

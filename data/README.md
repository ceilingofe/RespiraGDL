Los datos crudos no se suben al repo (`data/raw/*` está en `.gitignore`). Cada script en `scripts/` documenta de dónde baja cada archivo.

| Script | Qué hace | Salida |
| --- | --- | --- |
| `scripts/importar_simaj.py` | Convierte la base histórica oficial del SIMAJ (`raw/simaj/BD_<año>.xlsx`) al formato crudo del pipeline | `raw/sinaica_<estación>_<parámetro>_simaj.csv` |
| `scripts/descargar_sinaica.py` | Baja PM2.5, PM10 y clima horarios del SIMAJ vía SINAICA (dataset 39 del kit); alternativa para datos recientes | `raw/sinaica_<estación>_<parámetro>_<tipo>.csv` |
| `scripts/procesar_sinaica.py` | Limpia, junta y rellena huecos cortos | `processed/simaj_horario.csv`, `processed/resumen_datos.csv` |

## Base histórica del SIMAJ (la fuente que se usó)

Descargada el **2026-11-14** de la sección Datos → "Base histórica completa" del portal del
SIMAJ (aire.jalisco.gob.mx, que hoy vive en airejalisco.digital), SEMADET Jalisco:

| Archivo | URL |
| --- | --- |
| `BD_2020.xlsx` | https://airejalisco.digital/assets/files/historical/BD_2020.xlsx |
| `BD_2021.xlsx` | https://airejalisco.digital/assets/files/historical/BD_2021.xlsx |
| `BD_2022.xlsx` | https://airejalisco.digital/assets/files/historical/BD_2022.xlsx |
| `BD_2023.xlsx` | https://airejalisco.digital/assets/files/historical/BD_2023.xlsx |
| `BD_2024.xlsx` | https://airejalisco.digital/assets/files/historical/BD_2024.xlsx |

Van en `raw/simaj/` (no se suben al repo). SINAICA quedó como alternativa para datos
recientes; si la descarga automática falla, bajen el CSV a mano desde
https://sinaica.inecc.gob.mx/data.php. Guárdenlo en `raw/` con nombre `sinaica_*.csv` y estas
columnas: `estacion,estacion_id,parametro,fecha,hora,valor,valido`.

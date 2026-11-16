Los datos crudos no se suben al repo (`data/raw/*` está en `.gitignore`). Cada script en `scripts/` documenta de dónde baja cada archivo.

| Script | Qué hace | Salida |
| --- | --- | --- |
| `scripts/importar_simaj.py` | Convierte la base histórica oficial del SIMAJ (`raw/simaj/BD_<año>.xlsx`) al formato crudo del pipeline | `raw/sinaica_<estación>_<parámetro>_simaj.csv` |
| `scripts/descargar_sinaica.py` | Baja PM2.5, PM10 y clima horarios del SIMAJ vía SINAICA (dataset 39 del kit); alternativa para datos recientes | `raw/sinaica_<estación>_<parámetro>_<tipo>.csv` |
| `scripts/procesar_sinaica.py` | Limpia, junta y rellena huecos cortos | `processed/simaj_horario.csv`, `processed/resumen_datos.csv` |

## Base histórica del SIMAJ (la fuente que se usó)

### Reevaluación reproducida el 16 de noviembre de 2026

Se incluyen la serie pública ya limpia (`processed/simaj_horario.csv`), resumen CSV/JSON, predicciones de prueba y huellas de los cinco archivos oficiales (`processed/procedencia_simaj.json`). El modelo se reentrenó sin completar parcialmente huecos largos ni interpolar entre días. Son datos históricos, no lecturas ambientales actuales.

Para repetirlo, instala las versiones de `ml/requirements-reproducir.txt`. Descarga los cinco archivos de la tabla a `raw/simaj/` y comprueba sus SHA256 contra el manifiesto. Desde la raíz ejecuta:

```powershell
python data/scripts/importar_simaj.py
python data/scripts/procesar_sinaica.py
python ml/entrenar.py --estacion Miravalle --corte 2024-01-01
```

La importación conserva las banderas inválidas como ausentes. El resumen diario mayor a 25 usa los valores disponibles, sin exigir un mínimo diario de cobertura: es exploratorio, no una certificación normativa. El pipeline conserva topes de filtrado de 175 para PM2.5 y 600 para PM10; son decisiones de limpieza que pueden excluir episodios reales y requieren contraste con control de calidad.

### Descarga inicial y archivos oficiales

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

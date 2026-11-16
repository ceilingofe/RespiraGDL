# Método y datos de la reevaluación

> **Reevaluación, 16 nov 2026:** se descargaron de nuevo cinco archivos oficiales SIMAJ, se conservaron completos los huecos mayores de tres horas, se limitó la imputación al mismo día y se reentrenó Miravalle. Los resultados actuales sustituyen los previos y tienen huellas y versiones registradas. Las secciones de medición PMS5003/filtro siguen siendo un diseño futuro, no un experimento realizado. El montaje ESP32 + MQ-135 + LEDs + OLED no mide PM2.5. No hay revisión médica documentada. El segundo dataset y sus límites están en `docs/datasets.md`.

Los resultados de esta versión se generaron con el pipeline corregido y datos oficiales. Los artefactos completos están en `ml/resultados/` y la serie limpia en `data/processed/`.

## 1. Datos

| # | Dataset (catálogo del kit) | Institución | Periodo y cobertura | Qué datos tomamos | Para qué |
| --- | --- | --- | --- | --- | --- |
| 39 | Calidad del aire en Jalisco (SIMAJ / SINAICA) | SEMADET Jalisco / INECC | 2020-01-01 a 2024-12-31, horario, estaciones Miravalle, Las Pintas, Santa Fe y Centro (ZMG) | PM2.5 (µg/m³), PM10, temperatura, humedad relativa y viento por hora | **Describir el problema**: días con PM2.5 alto en las zonas de las escuelas. **Diseñar la solución**: entrenar el pronóstico a 24 h. **Comprobar resultados**: dato de afuera de referencia para compararlo con los sensores del salón |
| 11 | Anuario de morbilidad | Secretaría de Salud (DGE), ficha oficial IIEG | 2023, Jalisco, todas las edades | Casos nuevos de asma agregados por sexo | Contexto estatal preventivo, sin estimar asma infantil o causalidad ambiental |

Obtención del dataset 39: **base histórica oficial del SIMAJ** (SEMADET Jalisco), sección Datos → "Base histórica completa" de aire.jalisco.gob.mx (portal airejalisco.digital), archivos anuales `BD_2020.xlsx` a `BD_2024.xlsx` descargados el 2026-11-14 (URLs en `data/README.md`); se convierten al formato del pipeline con `data/scripts/importar_simaj.py`. Son los registros **oficiales publicados por SEMADET** (incluyen banderas de datos inválidos, que se descartan). Como alternativa para datos recientes queda `data/scripts/descargar_sinaica.py`, que usa el mismo servicio que la página pública sinaica.inecc.gob.mx/data.php, de la forma que documenta el paquete abierto `rsinaica`; no se usó porque el servidor de SINAICA estuvo caído los días previos a la entrega (bitácora en `data/raw/vigilante.log`).

### Limpieza (`data/scripts/procesar_sinaica.py`)

1. Valores negativos → vacío.
2. PM2.5 > 175 µg/m³ y PM10 > 600 µg/m³ → vacío. Son topes heurísticos del pipeline, no criterios de validez clínica o cumplimiento normativo. Pueden excluir episodios reales y requieren contraste con banderas de control de calidad.
3. Un valor por estación y hora; si hay duplicados, se promedian.
4. Solo huecos completos de hasta 3 horas, interiores al mismo día, se interpolan linealmente. Los huecos más largos o que cruzan medianoche quedan vacíos. El modelo no usa una jornada si le faltan más de 3 de las 8 horas escolares. Los conteos diarios del resumen son exploratorios y no aplican un criterio de completitud normativa por día.
5. Resultado: `data/processed/simaj_horario.csv` (175,381 filas horarias). La cobertura por estación queda en `data/processed/resumen_datos.csv` (copia en `docs/resumen_datos.csv`), 2020-01-01 a 2024-12-31:

| Estación | % de horas de PM2.5 con dato | PM2.5 promedio (µg/m³) | Días con promedio de 24 h > 25 µg/m³ (norma 2026) |
| --- | --- | --- | --- |
| Miravalle | 67.2 % | 25.3 | 566 |
| Las Pintas | 64.4 % | 39.2 | 802 |
| Santa Fe | 41.6 % | 27.3 | 400 |
| Centro | 68.3 % | 19.9 | 369 |

## 2. Medición en el salón (Aula Limpia)

- Dos nodos ESP32 con sensor PMS5003, uno **dentro** y otro **fuera** del salón. Cada uno manda su lectura de PM2.5 cada 60 s a la API.
- **% de protección = 1 − (PM2.5 dentro / PM2.5 fuera)**. Se calcula con el promedio de los últimos 60 min de cada sensor para quitar el ruido de lecturas sueltas. Se limita a 0–100 %. Si afuera hay menos de 10 µg/m³, no se calcula, porque con aire limpio el porcentaje no tiene sentido.
- Un salón con filtro y protección menor a 40 % genera una alerta de "revisar filtro encendido y puerta cerrada".
- No se realizó esa prueba física. Faltan sensores de partículas, ventilador y filtros; no se reporta una reducción medida por este equipo ni se inducirá humo cerca de personas.

## 3. Pronóstico de PM2.5 a 24 horas (`ml/entrenar.py`)

- **Qué se pronostica:** el promedio de PM2.5 de mañana de 7:00 a 14:00 (horario escolar) en Miravalle, estación del escenario ficticio. La reevaluación corresponde solo a esa estación; no se afirma haber reentrenado Las Pintas con el pipeline corregido.
- **Variables, conocidas al cierre de hoy:**
  - PM2.5 de hoy: promedio escolar, del día, de la tarde (15–20 h) y máximo.
  - Promedio escolar de ayer y media de 3 días.
  - Temperatura, humedad y viento de hoy.
  - Día de la semana y mes de mañana.
- **Línea base:** persistencia, "mañana será como hoy". Es lo mínimo que el modelo debe superar.
- **Modelo:** gradient boosting (`HistGradientBoostingRegressor`, scikit-learn). Acepta huecos en los datos de clima sin rellenarlos.
- **Validación:** partición **temporal**, sin revolver los días. Se entrena con 2020-01-05 a 2023-12-31 (903 días útiles) y se prueba con 2024-01-01 a 2024-12-30 (276 días útiles). La interpolación no cruza días. Se recargó el artefacto y se comprobaron sus 276 predicciones. Esto reduce riesgos de fuga temporal, sin equivaler a validación externa.
- **Métricas:**
  - Error absoluto medio (MAE) y RMSE en µg/m³.
  - % de días con el color del semáforo correcto.
  - % de días amarillo/rojo que sí se avisaron.
  - % de avisos que fueron falsa alarma.
- **Regla de uso:** si el modelo no le gana a la persistencia en MAE, el sistema usa la persistencia y se presenta como versión 1. Esto es el plan B del roadmap.

### Resultados (estación Miravalle, prueba 2024)

| Métrica | Persistencia (mañana = hoy) | Modelo (gradient boosting) |
| --- | --- | --- |
| Error absoluto medio (MAE, µg/m³) | 11.56 | **10.96** |
| Raíz del error cuadrático medio (RMSE, µg/m³) | 17.36 | **15.23** |
| Días con el color del semáforo correcto | 72.5 % | 69.2 % |
| Días amarillo/rojo que se avisaron | 78.7 % | 79.4 % |
| Avisos que resultaron falsa alarma | 21.8 % | 28.1 % |

Mejora del modelo sobre la persistencia en MAE: **5.2 %**. La regla técnica selecciona el modelo por MAE, pero sus falsas alarmas son mayores y su acierto de color menor. El costo de esos errores debe acordarse y validarse con la escuela antes de adoptar un sistema operativo. Gráfica actual: `ml/resultados/pred_vs_real.png`; predicciones en `ml/resultados/predicciones_prueba.csv`. Las diferencias respecto de las métricas previas incluyen limpieza y entorno, porque el entorno anterior no estaba registrado.

## 4. Semáforo y alertas

| Semáforo | PM2.5 (µg/m³) | Categoría | Qué hace la escuela |
| --- | --- | --- | --- |
| Verde | ≤ 25 | Buena / Aceptable | Recreo normal; vigilar a niños con asma |
| Amarillo | > 25 a 79 | Mala | Recreo adentro para niños con asma; filtro encendido |
| Rojo | > 79 | Muy mala o peor | Recreo adentro para todos; ventanas cerradas |

Los puntos de corte son los del Índice AIRE y SALUD de la **NOM-172-SEMARNAT-2023** (DOF, enero de 2024), Tabla 5, columna vigente **a partir de enero de 2026**: Buena ≤ 15, Aceptable > 15 a 25, Mala > 25 a 79, Muy mala > 79 a 130, Extremadamente mala > 130. La norma los aplica al promedio móvil ponderado de 12 horas; aquí se aplican al promedio de la jornada escolar (simplificación declarada). La línea de "norma" del tablero (`ALERTA_UMBRAL_PM25`) es el límite de PM2.5 a 24 horas de la **NOM-025-SSA1-2021** (DOF, 27 de octubre de 2021), que baja por etapas: 41 µg/m³ al entrar en vigor, 33 desde enero de 2024 y **25 desde enero de 2026** (promedio anual: 10). Se usa el valor vigente, 25 µg/m³.

## 5. Software

- Todo es software libre y corre en una laptop: FastAPI + SQLite, scikit-learn y React.
- La API guarda solo el **número** de alumnos con asma por grupo, sin nombres.
- Las lecturas simuladas quedan marcadas en la base.

## 6. Limitaciones y qué está simulado

- No hay PMS5003 en el montaje disponible. El MQ-135 no mide PM2.5. Los valores de dentro/fuera de la demo se identifican como simulados; el histórico SIMAJ no representa aire exterior actual.
- La base histórica del SIMAJ llega a diciembre de 2024, así que el modelo se entrenó y evaluó con 2020–2024. El servidor de SINAICA (datos recientes) estuvo caído los días previos a la entrega (intentos registrados en `data/raw/vigilante.log`, 2026-11-14), por lo que en la demo el dato de "hoy" que alimenta el pronóstico viene del sensor de afuera de la escuela, y la API lo marca con `desactualizado: true` cuando recurre a la serie histórica.
- El pronóstico es para la estación del SIMAJ, no para cada escuela. Dentro de una colonia el aire puede variar.
- La NOM-172 aplica sus cortes al promedio móvil ponderado de 12 h; aquí se aplican al promedio de la jornada escolar (7:00–14:00). Es una simplificación declarada.
- El sistema orienta y alerta; no diagnostica. La revisión médica de la guía sigue pendiente.

# Método y datos (borrador de Juan para el reporte científico)

> Damaris: esta es la sección de método. Los números entre `[ ]` se llenan cuando corran
> `ml/entrenar.py` con los datos reales; la tabla de resultados sale lista en
> `ml/resultados/metodo_resultados.md`. Entrega del reporte: domingo 12:00.

## 1. Datos

| # | Dataset (catálogo del kit) | Institución | Periodo y cobertura | Qué datos tomamos | Para qué |
| --- | --- | --- | --- | --- | --- |
| 39 | Calidad del aire en Jalisco (SIMAJ / SINAICA) | SEMADET Jalisco / INECC | [2022-01-01 a 2026-11-13], horario, estaciones Miravalle, Las Pintas, Santa Fe y Centro (ZMG) | PM2.5 (µg/m³), PM10, temperatura, humedad relativa y viento por hora | **Describir el problema**: días con PM2.5 alto en las zonas de las escuelas. **Diseñar la solución**: entrenar el pronóstico a 24 h. **Comprobar resultados**: dato de afuera de referencia para compararlo con los sensores del salón |
| 11 | Anuario de morbilidad | Secretaría de Salud (DGE / SINAVE) | [años], estatal (Jalisco) | Casos nuevos de asma en niños por grupo de edad | Describir el problema (carga de asma infantil) |
| 12 | Mortalidad general y por causa | INEGI / DGIS | 2024, Jalisco | Defunciones por influenza y neumonía, y por EPOC y asma | Describir el problema |
| 28 | Estadísticas educativas por municipio | SEJ / SEP | Ciclo [2024–2025], municipal | Matrícula de primaria en Guadalajara, Tlaquepaque y Tlajomulco | Dimensionar a cuántos alumnos puede llegar la solución |

Descarga del dataset 39: `data/scripts/descargar_sinaica.py`. Usa el mismo servicio que la página pública sinaica.inecc.gob.mx/data.php, de la forma que documenta el paquete abierto `rsinaica`. Se usaron datos **[crudos / validados]**.

### Limpieza (`data/scripts/procesar_sinaica.py`)

1. Valores negativos → vacío.
2. PM2.5 > 175 µg/m³ y PM10 > 600 µg/m³ → vacío. Son los mismos topes que aplica la página de SINAICA para descartar errores del equipo.
3. Un valor por estación y hora; si hay duplicados, se promedian.
4. Huecos de hasta 3 horas se interpolan linealmente. Los huecos más largos se dejan vacíos y el día no se usa si le faltan más de 3 de las 8 horas escolares.
5. Resultado: `data/processed/simaj_horario.csv`. La cobertura por estación queda en `data/processed/resumen_datos.csv`: [% de horas con dato, días con promedio 24 h > 45 µg/m³].

## 2. Medición en el salón (Aula Limpia)

- Dos nodos ESP32 con sensor PMS5003, uno **dentro** y otro **fuera** del salón. Cada uno manda su lectura de PM2.5 cada [60] s a la API.
- **% de protección = 1 − (PM2.5 dentro / PM2.5 fuera)**. Se calcula con el promedio de los últimos 60 min de cada sensor para quitar el ruido de lecturas sueltas. Se limita a 0–100 %. Si afuera hay menos de 10 µg/m³, no se calcula, porque con aire limpio el porcentaje no tiene sentido.
- Un salón con filtro y protección menor a 40 % genera una alerta de "revisar filtro encendido y puerta cerrada".
- Resultado de la prueba real: [fuera X µg/m³, dentro Y µg/m³, protección Z % durante N minutos; prueba de incienso en caja cerrada].
- Como referencia publicada, Arizona State University (2024) midió una baja de 43.3 % de PM2.5 dentro de 53 aulas con filtros caseros.

## 3. Pronóstico de PM2.5 a 24 horas (`ml/entrenar.py`)

- **Qué se pronostica:** el promedio de PM2.5 de mañana de 7:00 a 14:00 (horario escolar) en la estación del SIMAJ más cercana a la escuela ([Miravalle]).
- **Variables, conocidas al cierre de hoy:**
  - PM2.5 de hoy: promedio escolar, del día, de la tarde (15–20 h) y máximo.
  - Promedio escolar de ayer y media de 3 días.
  - Temperatura, humedad y viento de hoy.
  - Día de la semana y mes de mañana.
- **Línea base:** persistencia, "mañana será como hoy". Es lo mínimo que el modelo debe superar.
- **Modelo:** gradient boosting (`HistGradientBoostingRegressor`, scikit-learn). Acepta huecos en los datos de clima sin rellenarlos.
- **Validación:** partición **temporal**, sin revolver los días. Se entrena con [fechas] y se prueba con [fechas]. Así el modelo nunca ve el futuro.
- **Métricas:**
  - Error absoluto medio (MAE) y RMSE en µg/m³.
  - % de días con el color del semáforo correcto.
  - % de días amarillo/rojo que sí se avisaron.
  - % de avisos que fueron falsa alarma.
- **Regla de uso:** si el modelo no le gana a la persistencia en MAE, el sistema usa la persistencia y se presenta como versión 1. Esto es el plan B del roadmap.

[Pegar aquí la tabla de `ml/resultados/metodo_resultados.md` y la gráfica `ml/resultados/pred_vs_real.png`.]

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

- [Decir si el PMS5003 llegó. Si no llegó: el dato de fuera viene de la estación del SIMAJ y el de dentro de lecturas simuladas o grabadas (`backend/scripts/simular_nodos.py`), y así se dice en la demo.]
- El pronóstico es para la estación del SIMAJ, no para cada escuela. Dentro de una colonia el aire puede variar.
- Los datos crudos de SINAICA no están validados y pueden tener errores del equipo de medición.
- El sistema orienta y alerta; no diagnostica. La guía de crisis la valida un médico.

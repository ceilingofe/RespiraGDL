# Datos utilizados y trazabilidad

## 39 · Calidad del aire en Jalisco

SIMAJ / SEMADET Jalisco, histórico horario 2020-01-01 a 2024-12-31, estaciones Miravalle, Las Pintas, Santa Fe y Centro. Variables: PM2.5, PM10 y meteorología disponible. Se utiliza para caracterizar exposición local, delimitar el escenario y entrenar/evaluar el pronóstico. No mide interiores escolares.

URLs anuales y descarga: [`data/README.md`](../data/README.md). Limpieza: `data/scripts/procesar_sinaica.py`. Resumen preservado: [`resumen_datos.csv`](resumen_datos.csv). Método: [`metodo-y-datos.md`](metodo-y-datos.md).

Miravalle registra 566 días observados con promedio de 24 h >25 µg/m³ en todo 2020–2024, con 67.2 % de cobertura horaria. No se anualiza ese conteo ni se consideran los huecos como aire limpio. La cobertura no certifica suficiencia normativa por día; es un análisis exploratorio. El histórico no es calidad del aire actual.

Ese resumen se recalculó el 16 de noviembre de 2026 a partir de cinco archivos oficiales, conservando completos los huecos mayores de tres horas y sin interpolar entre días. URLs, huellas SHA256, conteos y versiones están en `data/processed/procedencia_simaj.json`. El resumen JSON que usa la web se genera junto al CSV para mantener cifras coherentes.

## 11 · Anuario de morbilidad — Jalisco

Fuente original: Secretaría de Salud / DGE, Anuario de Morbilidad 2023. Fuente oficial consultada: IIEG, *Enfermedades de la población de Jalisco en 2023*, 31 de marzo de 2025, página 3. Consulta de esta revisión: 16 de noviembre de 2026.

[Ficha oficial IIEG / DGE](https://iieg.gob.mx/ns/wp-content/uploads/2025/03/ficha_enfermedades_poblacion_jalisco_iieg_2023.pdf).

Se transcriben tres celdas agregadas de asma: total 13,613 casos nuevos, mujeres 8,263 y hombres 5,350. [Extracción con unidad, cobertura y fuente](../data/processed/morbilidad_jalisco_2023.csv). La suma por sexo coincide con el total.

Uso concreto: caracterizar el problema preventivo de Jalisco en la landing, `#/evidencia` y el reporte. No se utiliza para entrenar PM2.5. Son conteos estatales de todas las edades, no prevalencia infantil, pacientes únicos o casos causados por contaminación. No permiten estimar alumnos con asma en una escuela.

## Qué no se cuenta como dataset utilizado

Los conjuntos 12 y 28 se retiran de la lista de utilizados: no conservamos su extracción verificable. Salones ficticios y lecturas sintéticas tampoco cuentan como datos oficiales. El [kit oficial](https://solacyt.org/plataforma/site_media/docs/hackathon_kit_del_reto_2026.pdf) incluye los conjuntos 11 y 39; normas y manuales de hardware son referencias complementarias.

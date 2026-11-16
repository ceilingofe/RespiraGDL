# Respira GDL: prevención escolar y pronóstico de PM2.5

Hackathon Jalisco Internacional 2026 · Reto 02, Salud y Bienestar.
Equipo: Sergio, Juan, Carlos y Damaris. Revisión: 16 de noviembre de 2026.

## Resumen

Prototipo de software para organizar acciones escolares frente a contaminación en Miravalle, Guadalajara. Integra tablero, vista de maestra, demostración de avisos y pronóstico para la siguiente jornada escolar. Emplea dos conjuntos del catálogo: SIMAJ y Anuario de Morbilidad. El artefacto del modelo reporta 9.6 % de mejora en error absoluto medio frente a persistencia en 283 días de prueba de 2024. El montaje disponible muestra el semáforo en LEDs y OLED, y una señal MQ-135 sin calibrar. No se midió reducción de partículas ni impacto clínico; la escuela y sus usuarios son ficticios.

## Problema y población delimitada

El resumen SIMAJ registra en Miravalle 571 días observados de 2020–2024 con PM2.5 diario mayor a 25 µg/m³ y cobertura horaria de 68.6 %. Justifica explorar exposición local, sin tratar huecos como días limpios ni certificar cumplimiento normativo. El dataset de morbilidad proporciona contexto estatal de asma, sin inferir causalidad ni prevalencia infantil. Las fuentes y extracciones están en [`datasets.md`](datasets.md).

Usuarios propuestos: maestras, directivos y familias de primaria en Miravalle. No hay escuela participante, consentimiento recabado o prueba de usuarios documentados. Pregunta del prototipo: ¿podemos convertir evidencia ambiental y pronóstico en un flujo escolar comprensible que identifique simulación, antigüedad y falta de información?

## Objetivos e indicadores

1. Demostrar consulta de tablero → revisión de acciones → preparación de aviso.
2. Comparar pronóstico con persistencia mediante MAE, RMSE, detección de jornadas adversas y falsas alarmas.
3. Distinguir dato actual, histórico y simulación en el software y el semáforo.
4. Preparar un piloto de exposición y uso, sin atribuir resultados clínicos al prototipo.

## Método y reproducibilidad

La serie horaria SIMAJ se importa de los archivos oficiales 2020–2024. Los crudos no se distribuyen en el repositorio; sus URLs y scripts están en `data/README.md`. La limpieza, variables y limitaciones se describen en [`metodo-y-datos.md`](metodo-y-datos.md). El dataset de salud se conserva como tres observaciones agregadas con fuente y se utiliza para caracterizar el problema; no se mezcla con el entrenamiento ambiental.

El modelo predice el promedio de PM2.5 de 7:00 a 14:00 del día siguiente en Miravalle. El artefacto preservado usa 938 días de entrenamiento de 2020–2023 y 283 días de prueba de 2024-01-01 a 2024-12-30. Compara gradient boosting con persistencia («mañana = hoy»). Las cifras siguientes vienen de `ml/resultados/metricas.json`; no afirmamos haber repetido el entrenamiento completo durante esta revisión sin los crudos.

## Resultados retrospectivos

- MAE: persistencia 11.53 µg/m³; modelo 10.42 µg/m³; mejora registrada 9.6 %.
- RMSE: persistencia 17.47 µg/m³; modelo 14.89 µg/m³.
- Días adversos detectados: persistencia 79.1 %; modelo 83.5 %.
- Falsas alarmas: persistencia 21.4 %; modelo 26.3 %.
- Color correcto: persistencia 73.1 %; modelo 72.4 %.

El modelo mejora el error medio y detecta más jornadas adversas, pero empeora falsas alarmas y acierto de color. No presentamos una «precisión» única ni prometemos evitar crisis. Requiere evaluar datos recientes y costos de error antes de operar en una escuela.

En esta revisión se corrigió la limpieza para conservar completos los huecos mayores de tres horas. Los resúmenes y métricas guardados son anteriores a esa corrección: no deben atribuirse al pipeline corregido sin reprocesar los crudos y reentrenar. No se realizó aquí esa nueva evaluación.

## Prototipo y hardware real disponible

React ofrece tablero, plan escolar y acceso simulado por rol. FastAPI/SQLite recibe lecturas y entrega alertas. En Pages solo corre el frontend; sin API se muestran datos simulados. Algunas vistas dependen de rutas de integración que deben verificarse contra el backend instalado.

El montaje disponible utiliza ESP32 DevKit V1, MQ-135, tres LEDs y OLED HW-239. El MQ se conecta al GPIO34 mediante un divisor de tres resistencias de 1 kΩ. Se muestra como milivoltios, nunca como PM2.5, CO₂ o categoría médica. Los LEDs y OLED muestran el semáforo escolar de la API; las simulaciones parpadean y la falta de información hace parpadear los tres LEDs. El firmware ofrece pruebas manuales explícitamente simuladas.

No contamos con PMS5003, ventilador o filtros en este montaje. La comparación dentro/fuera de la demo es sintética; el filtro es diseño propuesto. La fórmula `1 − dentro/fuera` requiere sensores de partículas comparables y ventanas simultáneas, no voltajes del MQ. Compilar no equivale a verificar físicamente el circuito.

## Tres áreas de conocimiento

- Ingeniería de software y electrónica: prototipo, API, interfaz y manejo de desconexión.
- Ciencia de datos: limpieza, separación temporal, pronóstico y contraste con línea base.
- Salud pública: contexto preventivo, comunicación comprensible, privacidad y equidad.

La integración es el flujo de decisiones escolares, sin afirmar validación médica.

## Ética, consentimiento y equidad

La demo no debe capturar datos de menores reales. El acceso por rol no es autenticación de producción. Los planes se guardan en el navegador: no se comparten automáticamente con la maestra ni forman un expediente. Un grupo pequeño puede permitir reidentificación aun sin nombres.

Antes de un piloto se necesitan autorización escolar, información y consentimiento cuando corresponda, revisión profesional, control de acceso, retención y borrado definidos. No se capturan nombres, teléfonos, dosis o texto libre de pacientes. No se publicarán grupos pequeños identificables. Esto es un requisito pendiente, no una autorización ya obtenida.

OLED y LEDs facilitan consulta sin teléfono. El texto y la posición complementan el color. Deben existir alternativas impresas e institucionales para familias sin internet. No recibir datos nunca significa «aire bueno».

## Viabilidad y siguiente experimento

El software funciona en laptop y red local. Los $3,700 MXN del estimador son una referencia ilustrativa del diseño completo, no cotización ni gasto comprobado del montaje. La BOM requiere aclarar importes por unidad o partida y agregar mantenimiento, filtros, energía y conectividad antes de presupuestar una escuela.

Piloto propuesto, sin ejecutar:

1. Acordar escuela, responsables, revisión médica y consentimiento.
2. Conseguir dos sensores PM2.5, cotejarlos juntos y registrar cobertura/fallas.
3. Comparar periodos con/sin filtro y dentro/fuera, con horarios simultáneos y registro de ocupación, puertas y ventanas. No inducir humo cerca de personas.
4. Reportar concentraciones y diferencias con incertidumbre; definir antes cuándo descartar periodos incompletos.
5. Medir comprensión del semáforo, tareas completadas y avisos efectivamente recibidos. Son resultados operativos, no eficacia clínica.

## Limitaciones y conclusión

El histórico llega a 2024, hay datos faltantes y una estación no representa el interior de cada aula. Los cortes del semáforo se aplican a un promedio escolar distinto del procedimiento oficial completo. Faltan validación física, clínica, de usuarios y despliegue de producción.

La contribución demostrable es un prototipo reproducible que conecta evidencia local, evaluación temporal y comunicación escolar. Su siguiente paso verificable es un piloto de exposición y uso.

## Referencias

- [Kit oficial](https://solacyt.org/plataforma/site_media/docs/hackathon_kit_del_reto_2026.pdf), indicaciones generales y Reto 02.
- [IIEG / DGE, morbilidad 2023](https://iieg.gob.mx/ns/wp-content/uploads/2025/03/ficha_enfermedades_poblacion_jalisco_iieg_2023.pdf), página 3.
- [SIMAJ, base 2024](https://airejalisco.digital/assets/files/historical/BD_2024.xlsx); años anteriores y procesamiento en `data/README.md`.
- `ml/resultados/metricas.json`, `metodo_resultados.md` y `pred_vs_real.png`.
- [Winsen MQ-135](https://www.winsen-sensor.com/manual/mq135.html?lang=en), alimentación y acondicionamiento.
- [`uso-ia.md`](uso-ia.md), declaración de apoyo y revisión.

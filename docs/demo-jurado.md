# Recorrido para el jurado

La propuesta se centra en una decisión escolar: cómo organizar prevención con información incompleta y recursos limitados. El campus es un **laboratorio educativo**, no un gemelo digital calibrado. El proyecto no tiene eficacia clínica demostrada.

## Una demostración de cuatro minutos

1. Abre `#/simulador`, sin iniciar sesión ni depender de internet para datos. Presenta los seis salones y la etiqueta de simulación. Selecciona 3A y acerca el salón para señalar filtro, personas ilustrativas, OLED y semáforo.
2. Avanza 30 minutos con los mismos parámetros y compara la curva con el caso sin filtros. Explica que es un cálculo idealizado, no una medición de partículas del MQ.
3. Cambia el inventario a dos filtros y pulsa **Ensayar reparto de filtros**. El criterio matemático prioriza la reducción de exposición estimada en la próxima hora, ponderada por ocupación. No utiliza diagnósticos ni decide tratamientos. Contrasta reparto y recursos, no «vidas salvadas».
4. Desactiva **Dispositivo conectado**: aparece SIN DATOS. El modelo puede seguir calculando aunque el dispositivo no tenga información. Eso permite explicar por qué una desconexión no puede dejar un verde viejo.
5. Abre `#/evidencia`: dataset ambiental SIMAJ y dataset de morbilidad DGE/IIEG, periodos, cobertura y usos distintos. Muestra las métricas preservadas con sus límites, incluida la necesidad de recalcularlas tras corregir el pipeline.
6. Enseña el montaje físico solo después de comprobarlo. `verde`, `amarillo` y `rojo` por USB son pruebas simuladas; `vivo` consulta la API. El MQ-135 no mide PM2.5 ni CO₂. No provoques humo o gas.

## Cómo responde a los cinco criterios del Reto 02

- **Problema de Jalisco:** delimita Miravalle y utiliza contexto estatal de morbilidad, sin extrapolar a alumnos concretos.
- **Prototipo funcional:** recorrido público sin cuenta, simulación reproducible, tablero/API y actuador ESP32 con manejo explícito de fallos.
- **Dos datasets oficiales:** las extracciones y el uso concreto están documentados en `docs/datasets.md`. La simulación no cuenta como dataset oficial.
- **Tres áreas:** ingeniería para interfaz/actuador, ciencia de datos para evaluación temporal y salud pública para prevención y comunicación.
- **Ética:** ninguna captura real de menores, acceso simulado declarado, límites de reidentificación y Telegram, revisión/consentimiento pendientes antes de un piloto.

El kit oficial exige demostrar el uso de datos, no solo nombrar fuentes. No garantiza un resultado de premiación.

## Preguntas difíciles que conviene responder con claridad

**¿Qué medimos hoy?** El MQ entrega una señal eléctrica sin calibrar. Los resultados físicos de reducción de PM2.5 están pendientes.

**¿Es IA el mapa?** No. Es un modelo físico educativo y un algoritmo de reparto de recursos. El modelo de aprendizaje automático es el pronóstico retrospectivo separado; ambos se presentan con sus supuestos.

**¿Cuánto mejora la salud?** No lo hemos medido. El siguiente piloto mediría exposición, cobertura y comprensión antes de plantear resultados clínicos.

**¿Cuál es el costo?** Los $3,700 del estimador son una referencia del diseño previo. No son cotización ni gasto del montaje disponible; faltan confirmación de partidas, energía y mantenimiento.

**¿Qué ocurre sin internet?** El campus local funciona sin API, pero no recibe aire real. El hardware muestra SIN DATOS cuando falta comunicación y puede ensayarse por USB sin fingir un dato actual.

**¿Qué sigue?** Autorización escolar, revisión profesional, sensores PM2.5 cotejados y un piloto con protocolo previo, consentimiento y control de acceso. Grabación de video y publicación de Drive solo cuando existan los materiales finales.

Fuente: [kit oficial del Hackathon Jalisco Internacional 2026](https://solacyt.org/plataforma/site_media/docs/hackathon_kit_del_reto_2026.pdf), indicaciones generales y Reto 02.

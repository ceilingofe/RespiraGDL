# Manual de usuario

Respira GDL orienta y recuerda acciones escolares; no diagnostica ni reemplaza avisos oficiales o el plan médico individual. Las escuelas y alumnos de la demo son ficticios. No introduzcas datos reales de salud.

## Empieza por la evidencia

Abre **Evidencia** en el menú. Revisa fuentes, resultados y limitaciones. El histórico termina en 2024; no es una medición ambiental de hoy.

Elige **Ver la demo**. El acceso es simulado: director usa `director` en usuario y contraseña; maestra usa `maestra1` (cuentas `maestra1` a `maestra6`); familia usa `familia` en ambos campos. Estas cuentas no protegen datos reales.

## Dirección

1. Lee el aviso de origen de datos arriba de la pantalla. «Simulado» significa ensayo, no ambiente real.
2. Selecciona un salón para comparar dentro/fuera. El porcentaje no es una medición física del filtro de este equipo.
3. Verifica fecha y origen del pronóstico. Tener conexión con una API no garantiza un dato reciente.
4. Prueba preparar un aviso; distingue preparación, simulación y entrega comprobada. Pulsar un botón no demuestra recepción.

## Maestra y familias

La maestra revisa semáforo y tareas, marca acciones realizadas y observa si hubo error al guardar. La guía de crisis es orientativa, pendiente de revisión médica: prevalecen el plan individual autorizado y los procedimientos de la escuela. Ante emergencia solicita atención inmediata; no esperes al semáforo.

El formulario familiar ensaya opciones fijas guardadas **solo en ese navegador**. No envía automáticamente el plan al navegador de la maestra, no prescribe y no es un canal de emergencia. Borra las entradas de prueba desde la vista o eliminando los datos del sitio.

## Pantalla y LEDs

La OLED presenta salón, semáforo, conexión y señal MQ. PM2.5 viene de la API, nunca del MQ.

- Un LED fijo: fuente marcada como no simulada y vigente por la API.
- Un LED intermitente: simulación, identificada en pantalla.
- Tres LEDs intermitentes: **SIN DATOS**, no una categoría ambiental.
- `MQ ... mV`: señal eléctrica sin calibrar, no PM2.5, CO₂ o garantía de aire seguro.

El MQ requiere acondicionamiento del fabricante. No uses humo o gas como prueba frente a niños. [Guía completa del montaje](../firmware/semaforo-mq135/README.md).

## Si algo falla

- En GitHub Pages es normal usar respaldo simulado: no está desplegada la API.
- Si la API responde pero una vista usa respaldo, verifica que existan las rutas de integración que consume el frontend.
- Si parpadean tres LEDs, revisa red, URL real de la laptop y metadatos de vigencia. No uses localhost en el ESP32.
- Si la OLED queda en blanco, revisa 3.3 V, SDA/SCL y el comando serial `oled` para alternar controlador.
- Ante falta de datos, sigue el plan escolar y los avisos institucionales. El prototipo no garantiza vigilancia continua.

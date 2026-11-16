# Guion de demostración · aproximadamente cuatro minutos

La grabación se hace con el prototipo real que esté disponible. El semáforo físico se muestra solo después de probar el cableado. No se edita para aparentar una entrega de avisos o medición que no ocurrió. Mantener visible la etiqueta de simulación.

## 0:00–0:30 · Una decisión de una maestra

**Mostrar:** Inicio y la sección Evidencia.

**Decir:** «Una maestra en Miravalle necesita organizar la jornada cuando hay contaminación. Respira GDL reúne información ambiental, un plan escolar y un semáforo visible sin teléfono. Esta escuela es ficticia: hoy demostramos el software y un montaje electrónico, no una intervención médica ya validada».

## 0:30–1:05 · Dos fuentes que sí utilizamos

**Mostrar:** fuentes en Evidencia, sin convertir el histórico en una lectura de hoy.

**Decir:** «Usamos dos datasets del catálogo: calidad del aire SIMAJ para caracterizar la exposición y evaluar el pronóstico; y Anuario de Morbilidad para el contexto estatal de asma. Delimitamos Miravalle. El histórico llega a 2024 y tiene datos faltantes. Los registros estatales de salud no permiten estimar asma infantil en esta escuela».

## 1:05–1:50 · Tres acciones de la demo

**Recorrido alternativo recomendado:** antes del tablero, abrir Escuela 3D, avanzar el ensayo, ajustar inventario y ensayar el reparto. Desconectar el dispositivo virtual para mostrar SIN DATOS. Explicar que todo el campus es un modelo educativo ficticio y que su porcentaje no es una reducción física medida. El recorrido detallado está en `docs/demo-jurado.md`.

**Mostrar:** entrar como director, seleccionar 3A, después vista de maestra. Si falla una ruta de API, conservar visible el aviso de respaldo.

**Decir:** «Primero consulto el tablero y su origen. Después reviso las acciones del grupo. Finalmente preparo el aviso a familias. Aquí las lecturas y alumnos son simulados. Una marca guardada o un botón de envío no comprueba que una familia recibió un mensaje: eso se valida por separado. La guía orienta y siempre prevalece el plan médico individual».

## 1:50–2:35 · El semáforo que sí podemos montar

**Mostrar:** ESP32, tres LEDs, MQ-135, OLED. En el monitor serial, enviar `verde`, `amarillo` y `rojo`; la OLED debe mostrar PRUEBA SIMULADA. Después `vivo`; si no hay API vigente, mostrar SIN DATOS.

**Decir:** «Este es el actuador del salón: pantalla y LEDs. El modo de prueba cambia los colores y está marcado como simulado. Si falta información, no dejamos un verde viejo: indicamos SIN DATOS. El MQ-135 muestra milivoltios como señal sin calibrar; no mide PM2.5 ni CO₂. Por eso no convertimos su señal en la contaminación del tablero».

No generar humo ni gas. No filmar contraseñas o el monitor durante la configuración WiFi.

## 2:35–3:15 · Modelo con comparación honesta

**Mostrar:** sección de resultados y el archivo de métricas.

**Decir:** «El artefacto evaluado en 283 días de 2024 registró MAE de 10.42 frente a 11.53 de persistencia. Detectó más jornadas adversas, pero generó más falsas alarmas y acertó ligeramente menos colores. No lo resumimos en una precisión engañosa. Una corrección posterior de limpieza requiere recalcular estos resultados antes de atribuirlos al pipeline actual».

## 3:15–4:00 · Viabilidad y siguiente paso

**Mostrar:** limitaciones, diseño futuro del filtro y repositorio.

**Decir:** «El aporte es unir ciencia de datos, ingeniería y prevención escolar con un flujo comprensible. No tenemos aún sensores de partículas ni filtro montado: no afirmamos reducción física o menos crisis. El siguiente paso es un piloto autorizado con dos sensores PM2.5, mediciones comparables y evaluación de comprensión y recepción de avisos. El sistema no recopila datos reales de menores en esta demo. Usamos asistentes de IA como apoyo y el equipo debe revisar y explicar su trabajo».

## Antes de grabar

Comprobar carga del firmware, polaridad, alimentación, OLED y los tres LEDs; abrir Evidencia y las cuentas demo; confirmar qué rutas de la API están disponibles; preparar alternativa sin internet; desactivar notificaciones y ocultar credenciales. El video final debe mostrar el estado que realmente ocurrió. La publicación en YouTube y los permisos de Drive siguen pendientes hasta que se realicen y prueben.

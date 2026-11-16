# Verificación de la entrega · 16 de noviembre de 2026

La implementación se preparó sobre `main` actualizado con backend y bot integrados, en la rama `feat/demo-campus-y-semaforo`. El PR no integra por sí mismo la rama ni cambia el sitio de Pages hasta su incorporación a main.

## Software comprobado

- Backend: 74 pruebas pasaron con Python 3.12 y versiones registradas del modelo. Incluyen procedencia, datos vencidos, lectura de maestra, huecos largos, no imputación entre días y recarga del modelo real.
- Frontend: 10 pruebas pasaron. Verifican evolución/integral del simulador, no mutación, presupuesto, ocupación y consistencia de colores de ejemplo.
- Producción: `npm run build` pasó; el archivo JavaScript inicial es de aproximadamente 188 kB, con vistas cargadas por separado.
- Firmware: `pio run` pasó para `esp32dev`, ArduinoJson 7.4.2 y U8g2 2.36.5. Compilación no equivale a ensayo físico.
- Navegador: campus, selección de salones, controles, pausa, avance, reinicio y desconexión; vista de 360 px sin desbordamiento y movimiento reducido sin animación.
- PDFs: cinco archivos, 21 páginas en total. Pitch de ocho diapositivas e infografía de una página. Se revisaron renders y cifras actualizadas.

## Datos y modelo

Se descargaron de nuevo cinco archivos oficiales, se importaron 616,238 observaciones y se produjeron 175,381 filas horarias únicas por estación/hora. El modelo fue reentrenado con 903 días y evaluado con 276. El artefacto guardado se recargó y reprodujo las 276 predicciones y el MAE publicado. Los manifiestos conservan URLs, SHA256 y versiones.

Los porcentajes diarios son exploratorios por cobertura incompleta. La mejora actual del MAE es 5.2 %, con falsas alarmas mayores y acierto de color menor que persistencia. No hay validación externa ni clínica. El mapa educativo no genera estas métricas y no escribe datos en la API.

## Cómo repetir las comprobaciones

Desde la raíz:

```powershell
python -m pip install -r backend/requirements.txt
pytest backend/tests -q
```

Desde `frontend/`: `npm ci`, `npm test` y `npm run build`. Desde `firmware/semaforo-mq135/`: `pio run`. CI ejecuta estas tres áreas automáticamente en el PR.

## Pendientes que requieren evidencia externa

No se probó físicamente la placa/cableado, no se midieron partículas o reducción con filtro, y no se ejecutó un piloto escolar. La grabación del video, publicación de entregables en Drive y prueba de permisos quedan pendientes. El acceso por rol es de demostración; no se deben introducir datos reales de menores. No se enviaron mensajes de Telegram o correo durante estas comprobaciones.

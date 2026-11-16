# PDFs listos para revisar

- `reporte-cientifico-respira-gdl.pdf`: reporte científico con método, resultados preservados, fuentes, ética y limitaciones.
- `manual-usuario-respira-gdl.pdf`: recorrido para dirección, maestra y familias, señales del dispositivo y simulador de aulas.
- `guia-cableado-respira-gdl.pdf`: montaje ESP32 DevKit V1, divisor de tres resistencias de 1 kohm, OLED, pruebas y diagnóstico de fallas.
- `pitch-respira-gdl.pdf`: exactamente ocho diapositivas, formato 16:9.
- `infografia-respira-gdl.pdf`: una página A4 para compartir o imprimir.

## Regenerar con fuentes locales

Desde la raíz del repositorio, con Python 3.10 o posterior:

```powershell
python -m pip install reportlab pillow
python entregables/generar_pdfs.py
```

El generador también acepta `--output-dir` para elegir otra carpeta de salida. No necesita servicios, claves o conexión de red. Lee el reporte y manual de `docs/`, la guía de `firmware/semaforo-mq135/README.md` y los colores de `frontend/src/styles/tokens.css`. El pitch y la infografía tienen composición y texto editables en el mismo script. Las fuentes y capturas están en `entregables/assets/`.

Después de cambiar fuentes o contenido hay que regenerar y revisar visualmente todos los PDFs. La paginación puede variar con el contenido. El pitch y la infografía leen los números retrospectivos directamente de `ml/resultados/metricas.json` y el contexto ambiental del registro Miravalle en `data/processed/resumen_datos.json`. Los textos del reporte deben mantenerse consistentes con esos artefactos.

## Identidad y procedencia

Tipografía Poppins Regular y SemiBold, distribuida bajo la licencia SIL Open Font License incluida en `../assets/OFL-Poppins.txt`. Archivos originales del repositorio oficial [Google Fonts, Poppins](https://github.com/google/fonts/tree/main/ofl/poppins).

Identificador gráfico oficial del evento: [Hackathon Jalisco Internacional, SOLACYT](https://solacyt.org/plataforma/site_media/img/hackathon_wordmark.jpg). Se conserva su proporción sobre blanco. Su presencia identifica el evento y no implica aval médico o institucional del prototipo.

Las capturas corresponden a la aplicación del equipo. El campus, escuela, ocupantes y dispositivos ilustrados son simulados. No muestran una instalación física ni una escuela participante. Las referencias científicas y sus enlaces se conservan en el reporte y en `docs/datasets.md`.

## Alcance y revisión

Los PDFs recogen la evaluación retrospectiva del modelo reentrenado con la limpieza corregida, la falta de sensores PM2.5/filtro montado y la ausencia de validación clínica. Los históricos oficiales de 2020-2024 se reprocesaron, conservando los huecos largos y evitando imputaciones entre días. El voltaje MQ-135 no se transforma en PM2.5 o CO2. Las pruebas físicas siguen pendientes hasta realizarlas en el montaje real.

Se renderizaron las cinco salidas para revisar paginación, todas las diapositivas y la infografía. La revisión visual no equivale a comprobar hardware, datos actuales o eficacia sanitaria. Se usa `ohm` y `CO2` para evitar glifos que no incluye la fuente Poppins distribuida.

# Pronóstico de PM2.5 a 24 h

Pronostica el **promedio de PM2.5 de mañana de 7:00 a 14:00** en una estación del SIMAJ y lo traduce al semáforo de la escuela.

## Pasos (desde la raíz del repo)

```bash
pip install -r backend/requirements.txt matplotlib   # matplotlib solo para la gráfica

# 1. Datos (dataset 39). Primero ubica los IDs de Las Pintas y Santa Fe:
python data/scripts/descargar_sinaica.py --buscar
python data/scripts/descargar_sinaica.py --estacion Miravalle=106 --estacion Centro=102 \
    --estacion "Las Pintas=<id>" --estacion "Santa Fe=<id>" --desde 2022-01-01
python data/scripts/procesar_sinaica.py

# 2. Entrenar y evaluar
python ml/entrenar.py --estacion Miravalle

# (para probar el código sin datos reales; estos números NO van al reporte)
python ml/entrenar.py --sintetico
```

## Qué produce

| Archivo | Qué es | ¿Se sube? |
| --- | --- | --- |
| `ml/modelos/pronostico_pm25.joblib` | modelo + variables + métricas; lo carga la API | sí, es chico |
| `ml/resultados/metricas.json` | números para el reporte | sí |
| `ml/resultados/metodo_resultados.md` | tabla lista para la sección de método | sí |
| `ml/resultados/pred_vs_real.png` | gráfica real contra pronóstico en la prueba | sí |

## Método

- Las variables y el objetivo están en `backend/app/core/pronostico.py`. Ese mismo código lo usan el entrenamiento y la API, así que no se pueden desalinear.
- La línea base es la **persistencia** ("mañana = hoy"). El modelo es `HistGradientBoostingRegressor`.
- La partición es **temporal**: por defecto, el último 20 % de los días es la prueba. Se puede cambiar con `--corte`.
- Métricas: MAE y RMSE (µg/m³), % de días con el color del semáforo correcto, % de días amarillo/rojo avisados y % de falsas alarmas.
- Si el modelo no le gana a la persistencia, no se guarda y la API usa persistencia (plan B del roadmap).

Detalle para el reporte: `docs/metodo-y-datos.md`.

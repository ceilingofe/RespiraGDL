# Pronóstico de PM2.5 a 24 h

## Reevaluación del 16 de noviembre de 2026

Modelo y resultados actuales provienen de cinco archivos oficiales SIMAJ 2020–2024, con huecos largos completos y sin interpolar entre días. La serie limpia se incluye en el repositorio. Se conservan URLs, SHA256 y versiones; el artefacto se recargó para reproducir sus 276 predicciones de prueba. Usa Python 3.12 y las versiones fijadas en `requirements-reproducir.txt` (scikit-learn 1.9.1 para compatibilidad del joblib).

```powershell
python -m pip install -r backend/requirements.txt
python ml/entrenar.py --datos data/processed/simaj_horario.csv --estacion Miravalle --corte 2024-01-01
```

Resultado actual: MAE 10.96 frente a 11.56 de persistencia, mejora registrada de 5.2 %. El modelo tiene más falsas alarmas y menor acierto de color. Se reportan ambas cosas. Los cambios respecto de la ejecución anterior incluyen limpieza y entorno; no se atribuyen solo a la limpieza. No hay validación externa ni clínica.

Los pasos SINAICA de abajo son una alternativa de adquisición, no los usados en esta reevaluación. Para recrear los cinco archivos históricos sigue `data/README.md`. La selección temporal explícita de 2024 es la que sustenta estos resultados, no el corte automático del 20 %.

La gráfica entregada se genera desde las predicciones verificadas, usando fuentes y colores del proyecto y las fechas del día objetivo. Para recrearla sin reentrenar:

```powershell
python -m pip install -r ml/requirements-grafica.txt
python ml/graficar_resultados.py
```

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

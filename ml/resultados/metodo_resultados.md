## Resultados del pronóstico (estación Miravalle)

Entrenamiento: 2020-01-05 a 2023-12-31 (903 días).
Prueba: 2024-01-01 a 2024-12-30 (276 días), sin mezclar con el entrenamiento.
Objetivo: PM2.5 promedio de mañana de 7:00 a 14:00 (µg/m³).

| Métrica | Persistencia (mañana = hoy) | Modelo (gradient boosting) |
| --- | --- | --- |
| Error absoluto medio (MAE, µg/m³) | 11.56 | 10.96 |
| Raíz del error cuadrático medio (RMSE, µg/m³) | 17.36 | 15.23 |
| Días con el color del semáforo correcto | 72.5 % | 69.2 % |
| Días amarillo/rojo que se avisaron | 78.7 % | 79.4 % |
| Avisos que resultaron falsa alarma | 21.8 % | 28.1 % |

Mejora del modelo sobre la persistencia en MAE: **5.2 %**. En la demo se usa: **modelo**.

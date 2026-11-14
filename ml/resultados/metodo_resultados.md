## Resultados del pronóstico (estación Miravalle)

Entrenamiento: 2020-01-01 a 2023-12-31 (938 días).
Prueba: 2024-01-01 a 2024-12-30 (283 días), sin mezclar con el entrenamiento.
Objetivo: PM2.5 promedio de mañana de 7:00 a 14:00 (µg/m³).

| Métrica | Persistencia (mañana = hoy) | Modelo (gradient boosting) |
| --- | --- | --- |
| Error absoluto medio (MAE, µg/m³) | 11.53 | 10.42 |
| Raíz del error cuadrático medio (RMSE, µg/m³) | 17.47 | 14.89 |
| Días con el color del semáforo correcto | 73.1 % | 72.4 % |
| Días amarillo/rojo que se avisaron | 79.1 % | 83.5 % |
| Avisos que resultaron falsa alarma | 21.4 % | 26.3 % |

Mejora del modelo sobre la persistencia en MAE: **9.6 %**. En la demo se usa: **modelo**.

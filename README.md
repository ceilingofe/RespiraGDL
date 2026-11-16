# Respira GDL · Aulas que protegen a niños con asma

Proyecto del Hackathon Jalisco Internacional 2026, Reto 02 Salud y Bienestar.

Respira GDL es un prototipo de prevención escolar para consultar calidad del aire, preparar acciones y demostrar avisos a familias. Busca reducir exposición con filtros en una fase futura; **todavía no demuestra reducción física ni beneficios clínicos**. Combina:

- **Aula Limpia:** filtro casero (ventilador + 4 filtros MERV-13) y dos sensores PM2.5 con ESP32, uno dentro y otro fuera del salón.
- **Plan de asma escolar:** alertas al maestro, semáforo en el salón y guía paso a paso ante una crisis.
- **Pronóstico:** modelo de PM2.5 a 24 h con datos del SIMAJ/SINAICA y clima.

> No es una herramienta de diagnóstico. Orienta, recuerda y alerta. Esta demo no debe capturar datos reales de menores. El bot necesita identificadores de Telegram para entregar avisos: no son datos anónimos.

## Qué está simulado · plan B

La escuela Miravalle y sus alumnos son ficticios. El montaje disponible es **ESP32 DevKit V1 + MQ-135 + tres LEDs + OLED HW-239**: [firmware y cableado](firmware/semaforo-mq135/README.md). El MQ muestra milivoltios, no PM2.5 ni CO₂. Los LEDs representan el semáforo escolar de la API; no una medición de partículas de ese salón.

No contamos con PMS5003, ventilador ni filtros MERV-13 en este montaje. El filtro es un diseño propuesto y los valores dentro/fuera de la demo son simulados. El histórico SIMAJ termina en 2024 y no representa el exterior actual. El modelo guardado mejoró MAE en 5.2 %, con más falsas alarmas que persistencia; eso no demuestra menos crisis de asma.

GitHub Pages publica solo el frontend; la API corre en una laptop. El acceso por rol es simulado y los planes familiares son locales al navegador: **no introducir datos reales de salud**. Revisa la ruta pública `#/evidencia`, el [reporte](docs/reporte-cientifico.md) y el [manual](docs/manual-usuario.md).

## Diseño

La guía de diseño del proyecto está en [`docs/diseno/README.md`](docs/diseno/README.md) y los tokens en [`frontend/src/styles/tokens.css`](frontend/src/styles/tokens.css). Todo lo visual la sigue.

## Estructura

| Carpeta | Qué hay | Responsable |
| --- | --- | --- |
| `firmware/` | Código del nodo ESP32 + PMS5003 | Sergio |
| `hardware/` | Lista de materiales, diagramas y guía del filtro casero | Sergio |
| `backend/` | API FastAPI, base de datos, ingesta de SINAICA, alertas | Juan |
| `ml/` | Notebooks y modelo de pronóstico de PM2.5 | Juan |
| `data/` | Scripts de descarga y datos procesados (los crudos no se suben) | Juan |
| `frontend/` | Tablero de la escuela y vista del maestro | Carlos |
| `bot/` | Bot de alertas para familias (Telegram en la demo) | Carlos |
| `docs/` | Reporte científico, manual de usuario, datasets, uso de IA | Damaris |
| `entregables/` | Pitch, infografía, guion y enlace del video | Damaris + todos |

## Cómo correrlo

Para el jurado: abre **Escuela 3D** (`#/simulador`) desde Inicio. Es una simulación pública de seis salones con comparación de escenarios e inventario limitado, sin API ni credenciales. Luego abre **Evidencia** (`#/evidencia`) para distinguir el modelo educativo de las fuentes oficiales y resultados retrospectivos. El [recorrido del jurado](docs/demo-jurado.md) explica qué demostrar y qué no afirmar.

```bash
# backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend
cd frontend && npm install && npm run dev

# firmware (PlatformIO)
cd firmware/nodo-aire && cp include/config.example.h include/config.h && pio run -t upload
```

## Flujo de trabajo

- `main` siempre funciona y es lo que se entrega. Nadie sube directo a `main`.
- Cada tarea va en una rama `feat/<area>-<tema>` (ej. `feat/backend-alertas`) y entra por pull request con una revisión.
- Issues con la etiqueta de su área: `firmware`, `backend`, `ml`, `frontend`, `bot`, `docs`, `entregables`.

## Datasets del catálogo del kit

Se utilizan **39 Calidad del aire (SIMAJ)** y **11 Anuario de morbilidad**. El segundo se conserva como extracción agregada en `data/processed/morbilidad_jalisco_2023.csv`. [Fuentes y uso concreto](docs/datasets.md). Educación y mortalidad no se cuentan como utilizados sin una extracción verificable.

## Uso de inteligencia artificial

Ver `docs/uso-ia.md`. El equipo declara el uso de IA en la planeación, el código y los documentos.

## Equipo

Sergio · Juan · Carlos · Damaris

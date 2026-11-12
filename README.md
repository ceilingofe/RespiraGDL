# Respira GDL · Aulas que protegen a niños con asma

Proyecto del Hackathon Jalisco Internacional 2026, Reto 02 Salud y Bienestar.

Respira GDL baja el aire contaminado que respiran los niños dentro del salón y avisa a maestros y familias de niños con asma antes de un día de mala calidad del aire. Combina:

- **Aula Limpia:** filtro casero (ventilador + 4 filtros MERV-13) y dos sensores PM2.5 con ESP32, uno dentro y otro fuera del salón.
- **Plan de asma escolar:** alertas al maestro, semáforo en el salón y guía paso a paso ante una crisis.
- **Pronóstico:** modelo de PM2.5 a 24 h con datos del SIMAJ/SINAICA y clima.

> No es una herramienta de diagnóstico. Orienta, recuerda y alerta. Solo usa datos agregados o anónimos.

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

Ver `docs/datasets.md`: 39 Calidad del aire (SIMAJ/SINAICA), 11 Anuario de morbilidad, 28 Estadísticas educativas, 12 Mortalidad.

## Uso de inteligencia artificial

Ver `docs/uso-ia.md`. El equipo declara el uso de IA en la planeación, el código y los documentos.

## Equipo

Sergio · Juan · Carlos · Damaris

# Frontend Respira GDL

Landing, tablero de la escuela y vista del maestro. React 18 + Vite, sin más dependencias.

En vivo: https://ceilingofe.github.io/respiragdl/ (se publica solo en cada push a `main` que toque `frontend/`).

| Ruta | Qué es |
| --- | --- |
| `#/` | Landing con el hero rotativo de los 3 pilares |
| `#/tablero` | Tablero del director: semáforo, alertas por salón, gráfica fuera/dentro (Recharts), tabla de salones y pronóstico |
| `#/maestro` | Vista de celular de la maestra: semáforo, alumnos con asma, checklist del día y botón de crisis |

## Correrlo

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build    # genera dist/
```

## Datos

Todo sale de `src/data/demo.js` y **es simulado**. Busquen `TODO: CONECTAR A LA API`: cada `useState` arranca con un `MOCK_*` y cada página trae un `useEffect` con el `fetch` comentado (`/salones`, `/lecturas`, `/pronostico/manana`, `/salones/3B/hoy`). Para conectar: descomenten el fetch, borren el bloque `MOCK_*` y pongan la URL en `frontend/.env.local` como `VITE_API_URL=...`.

## Diseño

Todo el frontend sigue la [guía de diseño](../docs/diseno/README.md). `src/styles/tokens.css` tiene las variables y `src/styles/app.css` los componentes; no usen hex sueltos. Las ilustraciones de `src/art/Art.jsx` son SVG temporales hasta tener fotos con licencia.

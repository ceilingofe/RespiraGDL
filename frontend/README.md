# Frontend Respira GDL

Landing, tablero de la escuela y vista del maestro. React 18 + Vite, sin más dependencias.

En vivo: https://ceilingofe.github.io/respiragdl/ (se publica solo en cada push a `main` que toque `frontend/`).

| Ruta | Qué es |
| --- | --- |
| `#/` | Landing con el hero rotativo de los 3 pilares |
| `#/tablero` | Tablero de la escuela: salones fuera/dentro, % de protección, pronóstico y aviso a familias |
| `#/maestro` | Vista de celular del maestro: semáforo, plan de asma y guía de crisis |

## Correrlo

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build    # genera dist/
```

## Datos

Todo sale de `src/data/demo.js` y **es simulado**. Para conectar la API reemplacen esas constantes por llamadas a `GET /lecturas`, `GET /salones/{id}/proteccion` y `GET /alertas/hoy`.

## Diseño

Todo el frontend sigue la [guía de diseño](../docs/diseno/README.md). `src/styles/tokens.css` tiene las variables y `src/styles/app.css` los componentes; no usen hex sueltos. Las ilustraciones de `src/art/Art.jsx` son SVG temporales hasta tener fotos con licencia.

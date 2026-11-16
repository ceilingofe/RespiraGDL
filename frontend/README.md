# Frontend Respira GDL

## Escuela 3D y evidencia

Las rutas públicas `#/simulador` y `#/evidencia` permiten presentar el proyecto sin cuenta ni API. El campus isométrico muestra seis salones ficticios con personas ilustrativas, filtros, ESP32/OLED y semáforo. Puedes seleccionar aula, acercar, pausar, avanzar y reiniciar, cambiar exterior/ventanas/ocupación, ensayar desconexión y repartir un inventario limitado de filtros.

El motor `src/data/simulacion.js` resuelve un modelo educativo de mezcla perfecta e integra concentración × tiempo × ocupación. Los supuestos se muestran en la página y no están calibrados. No se alimenta con MQ-135 ni envía lecturas a la API. El reparto compara la próxima hora bajo los mismos supuestos, sin datos de diagnósticos. Las métricas de salud o eficacia clínica no se derivan de ese porcentaje.

Verificación: `npm test` ejecuta pruebas del motor con Node y `npm run build` comprueba la producción. Las vistas se cargan por separado para reducir el JavaScript inicial. El campus respeta movimiento reducido y ofrece selección alternativa y acercamiento para celular.

En esta versión la nota de API dice «Datos recibidos de la API» y advierte si hay un pronóstico histórico. No se infiere una medición en vivo solo porque una petición respondió. Las notas y rutas descritas más abajo corresponden al flujo base; estas aclaraciones prevalecen.

Landing, tablero de la escuela, Aula Limpia y vista del maestro. React 18 + Vite; la única otra dependencia es Recharts (gráfica del tablero).

En vivo: https://ceilingofe.github.io/respiragdl/ (se publica solo en cada push a `main` que toque `frontend/`).

| Ruta | Qué es |
| --- | --- |
| `#/` | Landing con el hero rotativo de los 3 pilares |
| `#/aula` | Aula Limpia (director): una tarjeta por salón con el semáforo del aire de adentro, si tiene filtro y su % de protección |
| `#/tablero` | Tablero del director: semáforo, alertas por salón, gráfica fuera/dentro (Recharts), tabla de salones y pronóstico |
| `#/maestro` | Vista de celular de la maestra de cada grupo: semáforo, alumnos con asma, checklist del día, factores a cuidar y expedientes del grupo (ventanas modales, sin identificar) y botón de crisis |
| `#/alumno` | Vista de la familia: llena, edita o borra el plan de asma de su hijo (sin nombre ni teléfono) |
| `#/entrar` | Inicio de sesión simulado |

## Acceso (simulado)

Cada rol solo entra a su pantalla; si abre otra, lo regresa a la suya. La landing es pública.

| Usuario | Contraseña | Pantalla |
| --- | --- | --- |
| `director` | `director` | `#/aula` al entrar, con botón a `#/tablero` y de regreso (ve cuántos planes hay por salón, solo el número) |
| `maestra1` … `maestra6` | igual al usuario | `#/maestro` de su grupo: 1° A, 2° A, 3° A, 4° B, 5° A, 6° B. Ve sus factores a cuidar y sus expedientes (sin identificar) en ventanas modales |
| `familia` | `familia` | `#/alumno` |

**No es seguridad real:** la página está en GitHub Pages y los usuarios están en `src/data/sesion.js`. El acceso real lo dará la API (`TODO: CONECTAR A LA API`). Los planes que captura la familia se guardan solo en el `localStorage` de ese navegador; los simulados están en `src/data/planes.js`.

## Correrlo

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build    # genera dist/
```

## Datos

La URL de la API va en `frontend/.env.local` como `VITE_API_URL=...` (ver `frontend/.env.example`). Al abrir una pantalla se consulta `GET /salud`: si responde, los datos salen de la API; si no, se usan los datos simulados de `src/data/demo.js`. Arriba de cada pantalla una nota dice de dónde salen los datos (regla 5 del kit):

| Nota | Cuándo |
| --- | --- |
| "Demo con datos simulados: no hay conexión con la API." | Sin API (GitHub Pages) |
| "Datos de la API con lecturas simuladas (sin sensores físicos)." | La API responde, pero algún nodo o el pronóstico usa lecturas simuladas |
| "Datos en vivo de los sensores y la API." | Todo viene de sensores reales |
| "Algunos datos no llegaron de la API; esos se muestran simulados." | Falló alguna ruta |

### Tablero y vista de la maestra (`src/data/datosApi.js` y `src/data/useDatos.js`)

| Qué | Ruta (se refresca cada minuto) |
| --- | --- |
| Encabezado y semáforo de hoy | `GET /escuelas/miravalle` |
| Tabla de salones, alertas de protección baja y tarjetas de Aula Limpia | `GET /salones?escuela=miravalle` |
| Gráfica del salón elegido | `GET /lecturas/serie?salon_id={id}` (existe en todas las versiones de la API; si la respuesta no tiene la forma `{h, fuera, dentro}`, se usa el respaldo) |
| Pronóstico de mañana | `GET /pronostico/manana` (si viene `desactualizado`, el botón de aviso se desactiva) |
| ¿Lecturas simuladas? | `GET /lecturas/nodos` (campo `simulada`) |
| Vista de la maestra | `GET /salones/{id}/hoy`; "Qué hacer hoy" se guarda con `POST /salones/{id}/tareas/{tarea}` |

Sin dato de un sensor, la tabla muestra "—" en vez de un número y un aviso dice qué salones no tienen lecturas en la última hora y la hora de la última lectura (de `GET /lecturas/nodos`). La API calcula fuera, dentro y protección con las lecturas de la última hora: para la demo, corran `python -m scripts.cargar_demo --lecturas` (en `backend/`) poco antes de presentar, o dejen corriendo `scripts.simular_nodos`. **Simulado aunque haya API:** el acceso por rol y los planes de asma de las familias. La guía de crisis no avisa sola a la familia (el sistema no guarda qué familia es de qué alumno): le indica a la maestra que llame al teléfono que ya tiene registrado la escuela.

### Aviso a familias (ya conectado)

El aviso a familias del tablero ya usa la API (`src/data/avisosApi.js` y `src/data/useAvisos.js`):

| Qué | Ruta | Sin API (GitHub Pages) |
| --- | --- | --- |
| Botón "Enviar aviso a familias" de la tarjeta de pronóstico | `POST /alertas/enviar` sin mensaje (la API usa su texto sugerido) | Se simula y dice "(simulado)" |
| "Enviar ahora" de la ventana | `POST /alertas/enviar` con el mensaje escrito | Se simula y dice "(simulado)" |
| Confirmación del envío | `GET /alertas/aviso` cada 4 s hasta que el bot lo marca enviado (máx. 2 min) | — |
| Hora del aviso diario y nota de la escuela | `GET`/`PUT /alertas/programacion` (la nota es `mensaje`; el bot la agrega debajo del pronóstico) | Se guardan en este navegador |

Al abrir el tablero se consulta `GET /salud`: si responde, todo va a la API y la pantalla deja de decir "(simulado)". Si la API responde pero no tiene una ruta, la pantalla muestra el error en vez de fingir que se envió. Los mensajes tienen máximo 600 caracteres, igual que la API.

## Diseño

Todo el frontend sigue la [guía de diseño](../docs/diseno/README.md). `src/styles/tokens.css` tiene las variables y `src/styles/app.css` los componentes; no usen hex sueltos. Las ilustraciones de `src/art/Art.jsx` son SVG temporales hasta tener fotos con licencia.

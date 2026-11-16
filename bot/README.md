# Bot de alertas para familias

Bot de Telegram (gratis) que avisa a las familias de alumnos con asma el pronóstico de mañana (semáforo y PM2.5) y reparte los avisos que mandan el director o la maestra desde el tablero. Si el día viene malo, recuerda el inhalador y el plan de acción.

El bot no da diagnósticos: solo avisa y recuerda seguir el plan de acción de cada alumno.

## Correrlo

```bash
cd bot
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # y pegar el token de @BotFather en TELEGRAM_TOKEN
python bot.py
```

Para el pronóstico real, levanten también la API de Juan (`backend/README.md`) y pongan su URL en `API_URL`. Sin API el bot funciona con datos de ejemplo y lo dice en cada mensaje.

## Comandos

| Mensaje | Respuesta |
| --- | --- |
| `/start` o `/alta` | Registra a la familia y le pide, con botones, los grupos de sus hijos (puede marcar varios). No pide nombres |
| `/grupos` | Cambia los grupos |
| `/manana` | Pronóstico de mañana solo a quien lo pide |
| `/simular` | Simula el aviso a **toda la escuela** con el pronóstico actual |
| `/simular rojo` · `amarillo` · `verde` | Lo mismo forzando ese color (PM2.5 de ejemplo: 95, 40, 18) |
| `/simular 3A` · `/simular amarillo 3A` | Simula el aviso solo a las familias de ese grupo, como lo haría la maestra |
| `/hora` · `/hora 06:30` | Muestra o cambia la hora del aviso automático (hora de Guadalajara). El cambio también se guarda en el tablero |
| `/salir` | Deja de recibir avisos y borra los datos de la familia |
| `1` | Registra que un niño tuvo síntomas hoy (anónimo: solo se cuenta) y responde "Gracias. Esto ayuda a medir si el proyecto funciona." |

Grupos: 1A, 2A, 3A, 4B, 5A, 6B (los mismos del frontend y del backend).

## De dónde salen los datos

| Qué | Fuente | Si no está |
| --- | --- | --- |
| Pronóstico de mañana | `GET /pronostico` de la API (día "Mañana") | Datos de ejemplo (PM2.5 71) con la nota "Datos de ejemplo". Si la API dice `simulado: true` (lecturas de prueba), se muestra con la nota "Datos de prueba" |
| Semáforo | Cortes de la NOM-172-SEMARNAT-2023: verde ≤25, amarillo ≤79, rojo >79 µg/m³ (iguales a `backend/app/core/semaforo.py`) | — |
| Avisos del tablero y de la maestra | `GET /alertas/aviso/pendientes` cada `INTERVALO_AVISOS` s; luego `POST /alertas/aviso/{id}/enviado` con `{"familias": n}` | El bot lo anota una vez en el log y sigue reintentando en silencio |
| Familias suscritas | Archivo local; copia en la API con `POST /suscripciones` (al registrarse, al cambiar grupos y al arrancar el bot) y `DELETE /suscripciones/{chat_id}` (con `/salir` o si bloquean el bot) | El bot sigue con su archivo |
| Reportes de síntomas (`1`) | Conteo local del día; copia en la API con `POST /reportes-sintomas` (con `grupo` solo si la familia marcó uno) | El bot sigue con su conteo |
| Hora del aviso diario | `GET /alertas/programacion` cada minuto (la que guarda el tablero) | `HORA_AVISO` de `bot/.env` |

- **Aviso automático:** todos los días a las `HORA_AVISO` (07:00 si no se pone). **No se manda** si el pronóstico real no está disponible, está desactualizado o la API dice que es `simulado`: nunca sale con datos de ejemplo ni de prueba. Por si la API no trae `simulado`, el bot también revisa `GET /lecturas/nodos`: si el pronóstico sale del sensor de afuera y ese nodo tiene lecturas simuladas, no lo manda. Antes de usar sensores reales, borren las simuladas con `python -m scripts.cargar_demo --borrar-simuladas` (en `backend/`).
- **Mensaje de la escuela:** si el tablero guardó un mensaje (`GET /alertas/programacion`), el aviso diario y `/simular` lo agregan debajo del pronóstico como "Mensaje de la escuela". No reemplaza al semáforo ni al PM2.5, que siempre son los del día. Sin pronóstico real no sale aunque haya mensaje; para eso el tablero tiene "Enviar ahora".
- **Avisos con grupo:** si el aviso trae `grupo` (ej. `"3A"`), solo llega a las familias que marcaron ese grupo; sin grupo, a toda la escuela.
- **Un aviso no se repite:** el bot recuerda los ids que ya repartió, aunque falle el marcado en la API.

## Datos guardados

Las familias se guardan en `bot/datos/familias.json` para no perderlas al reiniciar. Solo contiene el número de chat de Telegram y los grupos marcados, el conteo de reportes de síntomas **del día** y los ids de avisos repartidos. **`bot/datos/` está en `.gitignore`: nunca se sube al repo.** Si una familia bloquea el bot o escribe `/salir`, se borra.

La API (PR #38 de Juan) guarda una copia de las suscripciones (solo chat y grupos) y el conteo de reportes para el tablero; el archivo local sigue mandando para que el bot funcione sin API.

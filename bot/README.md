# Bot de alertas para familias

Demo con Telegram (gratis). Mensaje diario a las 7:00 con el semáforo y, si es rojo, recordatorio de inhalador y plan de acción.

## Correrlo

```bash
cd bot
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # y pegar el token de @BotFather en TELEGRAM_TOKEN
python bot.py
```

## Qué hace hoy (datos simulados)

| Mensaje | Respuesta |
| --- | --- |
| `/start` | Bienvenida |
| `/manana` | Simula el mensaje de las 7:00: semáforo amarillo, PM2.5 71 |
| `1` | Registra que un niño tuvo síntomas (solo cuenta, sin nombres) |

Todo lo simulado está marcado con `TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ` en `bot.py`.
Endpoints esperados: `GET /alertas/hoy`, `POST /reportes-sintomas`, `POST /suscripciones`.

El envío automático a las 7:00 necesita `python-telegram-bot[job-queue]`; por ahora se simula con `/manana`.

El bot no da diagnósticos: solo avisa y recuerda seguir el plan de acción de cada alumno.

# Bot de alertas para familias

Demo con Telegram (gratis). Aviso a las familias con el pronóstico de mañana (semáforo y PM2.5) y, si es rojo, recreo adentro y recordatorio de inhalador y plan de acción.

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
| `/start` | Bienvenida; registra el chat para recibir avisos |
| `/manana` | Muestra el pronóstico de mañana solo a quien lo pide: rojo, PM2.5 71 |
| `/simular` | Simula el envío del aviso a **todas** las familias registradas (como el botón "Enviar aviso a familias" del tablero) |
| `/simular verde` · `amarillo` · `rojo` | Lo mismo, forzando ese color para probar los tres mensajes |
| `1` | Registra que un niño tuvo síntomas (solo cuenta, sin nombres) |

Todo lo simulado está marcado con `TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ` en `bot.py`.
Endpoints esperados: `GET /pronostico/manana`, `POST /alertas/enviar`, `GET`/`POST /suscripciones`, `POST /reportes-sintomas`.

El envío automático a las 7:00 necesita `python-telegram-bot[job-queue]`; por ahora se simula con `/simular`.

Para probar el envío a varias familias: abran el bot desde 2 o 3 cuentas de Telegram, manden `/start` en cada una y luego `/simular` desde cualquiera. Los chats viven en memoria: si reinician el bot, cada cuenta debe mandar `/start` otra vez.

El bot no da diagnósticos: solo avisa y recuerda seguir el plan de acción de cada alumno.

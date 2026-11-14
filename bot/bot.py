"""Bot de Telegram de Respira GDL (demo con datos simulados).

Comandos:
  /start            registra el chat para recibir avisos y explica cómo funciona
  /manana           muestra el pronóstico de mañana (semáforo + PM2.5) solo a quien lo pide
  /simular [color]  simula el envío del aviso a TODAS las familias registradas, como el botón
                    "Enviar aviso a familias" del tablero. color = verde | amarillo | rojo (por defecto
                    el del pronóstico)
  /hora [HH:MM]     muestra o cambia la hora del aviso automático diario (hora de Guadalajara)
  "1"               la familia avisa que su hijo/a tuvo síntomas; solo se cuenta, no se guarda nada personal

Correr:  python bot.py   (lee TELEGRAM_TOKEN de bot/.env)
"""

import logging
import os
import re
from datetime import time, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv(Path(__file__).with_name(".env"))
# Acepta los dos nombres: TELEGRAM_TOKEN (bot/.env.example) o TELEGRAM_BOT_TOKEN (.env.example de la raíz).
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("respira-bot")

# ---------------------------------------------------------------------
# TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
# Endpoint esperado: GET {API_URL}/pronostico/manana  (el mismo que usa el tablero)
# Reemplazar por algo como:
#   requests.get(f"{API_URL}/pronostico/manana", timeout=5).json()
# Mismos valores que MOCK_PRONOSTICO en frontend/src/data/demo.js.
# ---------------------------------------------------------------------
MOCK_PRONOSTICO_MANANA = {
    "escuela": "Esc. Prim. Miravalle T/M",
    "semaforo": "rojo",
    "pm25": 71,
}
# --- FIN MOCK PRONÓSTICO ---

# TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
# PM2.5 de ejemplo para /simular con otro color. Con la API, /simular usa el pronóstico real.
MOCK_PM25_POR_COLOR = {"verde": 18, "amarillo": 40, "rojo": 71}

# TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
# Hoy los chats y los reportes viven en memoria y se pierden al reiniciar.
# Mañana: POST {API_URL}/suscripciones y POST {API_URL}/reportes-sintomas
CHATS: set[int] = set()
REPORTES_HOY = 0

ICONO = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}
CONSEJO = {
    "verde": "Recreo normal al aire libre.",
    "amarillo": "Si su hijo o hija tiene asma, revise que lleve su inhalador y su plan de acción.",
    "rojo": (
        "El recreo y la educación física serán adentro. "
        "Revise que lleve su inhalador y su plan de acción."
    ),
}


def mensaje_aviso(pronostico: dict) -> str:
    """Texto del aviso a familias sobre el día de mañana."""
    color = pronostico["semaforo"]
    return (
        f"Aviso de Respira GDL · {pronostico['escuela']}\n\n"
        f"{ICONO.get(color, '')} Pronóstico para mañana: {color.upper()}\n"
        f"PM2.5 esperado: {pronostico['pm25']} µg/m³\n\n"
        f"{CONSEJO.get(color, '')}\n\n"
        "Si su hijo o hija tuvo tos, silbido en el pecho o le faltó el aire hoy, responda 1.\n"
        "Esto no es un diagnóstico; ante cualquier duda consulte a su médico."
    )


def obtener_pronostico() -> dict:
    # TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    return MOCK_PRONOSTICO_MANANA


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    CHATS.add(update.effective_chat.id)
    # TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    # requests.post(f"{API_URL}/suscripciones", json={"chat_id": update.effective_chat.id}, timeout=5)
    await update.message.reply_text(
        "Hola, soy el bot de Respira GDL. Cuando el aire de mañana venga malo le avisaré "
        "con el semáforo de la escuela.\n\n"
        "/manana muestra el pronóstico de mañana.\n"
        "/simular envía un aviso de prueba a todas las familias registradas."
    )


async def manana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(mensaje_aviso(obtener_pronostico()))


async def simular(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simula el envío masivo que hará el backend (o el botón del tablero) a las familias."""
    pronostico = dict(obtener_pronostico())
    if context.args:
        color = context.args[0].lower()
        if color not in ICONO:
            await update.message.reply_text("Use /simular, /simular verde, /simular amarillo o /simular rojo.")
            return
        pronostico.update(semaforo=color, pm25=MOCK_PM25_POR_COLOR[color])

    CHATS.add(update.effective_chat.id)  # quien prueba también recibe el aviso
    texto = "[SIMULACIÓN]\n" + mensaje_aviso(pronostico)
    enviados = 0
    # TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    # Con backend: la lista de chats sale de GET {API_URL}/suscripciones y el envío real lo dispara
    # POST {API_URL}/alertas/enviar (el mismo que llama el botón del tablero).
    for chat_id in list(CHATS):
        try:
            await context.bot.send_message(chat_id=chat_id, text=texto)
            enviados += 1
        except TelegramError as e:
            log.warning("No se pudo enviar a un chat: %s", e)
    log.info("Aviso simulado (%s) enviado a %s chats", pronostico["semaforo"], enviados)
    await update.message.reply_text(f"Aviso simulado enviado a {enviados} familia(s) registrada(s).")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global REPORTES_HOY
    texto = (update.message.text or "").strip()
    if texto == "1":
        REPORTES_HOY += 1
        # TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
        # requests.post(f"{API_URL}/reportes-sintomas", json={"escuela": "miravalle"}, timeout=5)
        log.info("Reporte de síntomas recibido (total hoy: %s)", REPORTES_HOY)
        await update.message.reply_text(
            "Gracias, quedó registrado. La escuela verá cuántos niños tuvieron síntomas hoy, "
            "sin nombres.\n\nSi le cuesta hablar, tiene los labios azulados o no mejora con "
            "su inhalador, llame al 911."
        )
    else:
        await update.message.reply_text(
            "Responda 1 si su hijo o hija tuvo síntomas hoy, o escriba /manana para ver el pronóstico."
        )


# ---------------------------------------------------------------------
# Aviso automático diario
# ---------------------------------------------------------------------
# Guadalajara está en UTC-6 todo el año (México quitó el horario de verano en 2022).
ZONA_GDL = timezone(timedelta(hours=-6), "Guadalajara")
NOMBRE_TRABAJO = "aviso-diario"
# TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
# Hoy la hora vive en memoria (arranca con HORA_AVISO de bot/.env).
# Con backend: leerla de GET {API_URL}/alertas/programacion, la misma que guarda el tablero.
HORA_AVISO = os.getenv("HORA_AVISO", "07:00")


def leer_hora(texto: str) -> time | None:
    """Convierte "7:30" o "07:30" en un time de Guadalajara; None si no es válido."""
    m = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", texto.strip())
    if not m:
        return None
    return time(int(m.group(1)), int(m.group(2)), tzinfo=ZONA_GDL)


async def enviar_aviso_diario(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lo llama el JobQueue a la hora programada: manda el aviso a todas las familias registradas."""
    texto = mensaje_aviso(obtener_pronostico())
    enviados = 0
    for chat_id in list(CHATS):
        try:
            await context.bot.send_message(chat_id=chat_id, text=texto)
            enviados += 1
        except TelegramError as e:
            log.warning("No se pudo enviar a un chat: %s", e)
    log.info("Aviso diario enviado a %s chats", enviados)


def programar_aviso(job_queue, hora: time) -> None:
    """Quita la programación anterior y deja una sola a la hora indicada."""
    for job in job_queue.get_jobs_by_name(NOMBRE_TRABAJO):
        job.schedule_removal()
    job_queue.run_daily(enviar_aviso_diario, time=hora, name=NOMBRE_TRABAJO)


async def hora(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global HORA_AVISO
    if context.job_queue is None:
        await update.message.reply_text(
            "El aviso automático no está activo: falta instalar APScheduler (pip install -r requirements.txt)."
        )
        return
    if not context.args:
        await update.message.reply_text(
            f"El aviso automático se envía todos los días a las {HORA_AVISO} (hora de Guadalajara).\n"
            "Para cambiarla escriba, por ejemplo: /hora 06:30"
        )
        return
    nueva = leer_hora(context.args[0])
    if nueva is None:
        await update.message.reply_text("Hora no válida. Use el formato HH:MM, por ejemplo: /hora 06:30")
        return
    programar_aviso(context.job_queue, nueva)
    HORA_AVISO = nueva.strftime("%H:%M")
    # TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    # requests.put(f"{API_URL}/alertas/programacion", json={"hora": HORA_AVISO}, timeout=5)
    log.info("Aviso diario reprogramado a las %s", HORA_AVISO)
    await update.message.reply_text(f"Listo. El aviso automático se enviará todos los días a las {HORA_AVISO}.")


def main() -> None:
    if not TOKEN:
        raise SystemExit("Falta TELEGRAM_TOKEN. Copie bot/.env.example a bot/.env y ponga el token de @BotFather.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("manana", manana))
    app.add_handler(CommandHandler("simular", simular))
    app.add_handler(CommandHandler("hora", hora))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    if app.job_queue is None:
        log.warning("Sin APScheduler: no habrá aviso automático. Corra pip install -r requirements.txt")
    else:
        inicial = leer_hora(HORA_AVISO)
        if inicial is None:
            raise SystemExit(f"HORA_AVISO no válida en bot/.env: {HORA_AVISO!r}. Use HH:MM, por ejemplo 07:00.")
        programar_aviso(app.job_queue, inicial)
        log.info("Aviso automático programado todos los días a las %s (Guadalajara)", HORA_AVISO)
    log.info("Bot corriendo. Ctrl+C para detener.")
    app.run_polling()


if __name__ == "__main__":
    main()

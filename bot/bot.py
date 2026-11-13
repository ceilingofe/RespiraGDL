"""Bot de Telegram de Respira GDL (demo con datos simulados).

Comandos:
  /start            registra el chat para recibir avisos y explica cómo funciona
  /manana           muestra el pronóstico de mañana (semáforo + PM2.5) solo a quien lo pide
  /simular [color]  simula el envío del aviso a TODAS las familias registradas, como el botón
                    "Enviar aviso a familias" del tablero. color = verde | amarillo | rojo (por defecto
                    el del pronóstico)
  "1"               la familia avisa que su hijo/a tuvo síntomas; solo se cuenta, no se guarda nada personal

Correr:  python bot.py   (lee TELEGRAM_TOKEN de bot/.env)
"""

import logging
import os
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


def main() -> None:
    if not TOKEN:
        raise SystemExit("Falta TELEGRAM_TOKEN. Copie bot/.env.example a bot/.env y ponga el token de @BotFather.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("manana", manana))
    app.add_handler(CommandHandler("simular", simular))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    log.info("Bot corriendo. Ctrl+C para detener.")
    app.run_polling()


if __name__ == "__main__":
    main()

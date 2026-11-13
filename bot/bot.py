"""Bot de Telegram de Respira GDL (demo con datos simulados).

Comandos:
  /start   registra el chat y explica cómo funciona
  /manana  simula el mensaje de las 7:00 (semáforo + PM2.5)
  "1"      la familia avisa que su hijo/a tuvo síntomas; solo se cuenta, no se guarda nada personal

Correr:  python bot.py   (lee TELEGRAM_TOKEN de bot/.env)
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv(Path(__file__).with_name(".env"))
# Acepta los dos nombres: TELEGRAM_TOKEN (bot/.env.example) o TELEGRAM_BOT_TOKEN (.env.example de la raíz).
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("respira-bot")

# ---------------------------------------------------------------------
# TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
# Endpoint esperado: GET {API_URL}/alertas/hoy
# Reemplazar por algo como:
#   requests.get(f"{API_URL}/alertas/hoy", timeout=5).json()
# ---------------------------------------------------------------------
MOCK_ALERTA_HOY = {
    "escuela": "Esc. Prim. Miravalle T/M",
    "semaforo": "amarillo",
    "pm25": 71,
}
# --- FIN MOCK ALERTA ---

# TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
# Hoy los chats y los reportes viven en memoria y se pierden al reiniciar.
# Mañana: POST {API_URL}/suscripciones y POST {API_URL}/reportes-sintomas
CHATS: set[int] = set()
REPORTES_HOY = 0

ICONO = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}
CONSEJO = {
    "verde": "Recreo normal al aire libre.",
    "amarillo": "Si su hijo o hija tiene asma, revise que lleve su inhalador y su plan de acción.",
    "rojo": "El recreo será adentro. Revise que lleve su inhalador y su plan de acción.",
}


def mensaje_matutino(alerta: dict) -> str:
    color = alerta["semaforo"]
    return (
        f"Buenos días. {ICONO.get(color, '')} Semáforo de hoy en {alerta['escuela']}: "
        f"{color.upper()}\n"
        f"PM2.5 esperado: {alerta['pm25']} µg/m³\n\n"
        f"{CONSEJO.get(color, '')}\n\n"
        "Si su hijo o hija tuvo tos, silbido en el pecho o le faltó el aire hoy, responda 1.\n"
        "Esto no es un diagnóstico; ante cualquier duda consulte a su médico."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    CHATS.add(update.effective_chat.id)
    await update.message.reply_text(
        "Hola, soy el bot de Respira GDL. Cada mañana a las 7:00 le enviaré el semáforo "
        "de calidad del aire de la escuela.\n\nPara ver el mensaje de hoy escriba /manana."
    )


async def manana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Simula el envío de las 7:00. Con la API: alerta = obtener_alerta_hoy()
    alerta = MOCK_ALERTA_HOY  # TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    await update.message.reply_text(mensaje_matutino(alerta))


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
        await update.message.reply_text("Responda 1 si su hijo o hija tuvo síntomas hoy, o escriba /manana.")


def main() -> None:
    if not TOKEN:
        raise SystemExit("Falta TELEGRAM_TOKEN. Copie bot/.env.example a bot/.env y ponga el token de @BotFather.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("manana", manana))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    log.info("Bot corriendo. Ctrl+C para detener.")
    app.run_polling()


if __name__ == "__main__":
    main()

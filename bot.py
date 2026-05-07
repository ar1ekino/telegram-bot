import os
import random
import json
import asyncio

from aiohttp import web

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
GIRL_NAME = "Танюша"

AUTO_KEY = "auto_enabled"
TIRED_KEY = "user_tired"

STATE_FILE = "state.json"

WEBHOOK_PATH = f"/webhook/{TOKEN}"
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render сам даёт

# ================= STATE =================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {AUTO_KEY: False, TIRED_KEY: False}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {AUTO_KEY: False, TIRED_KEY: False}


def save_state(data):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except:
        pass

# ================= KEYBOARD =================

def keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💌 Сейчас")],
            [KeyboardButton("🩺 После смены")],
            [KeyboardButton("😂 Шутка")],
        ],
        resize_keyboard=True
    )

# ================= CONTENT =================

def generate_compliment():
    return random.choice([
        f"{GIRL_NAME}, ты невероятная 💖",
        f"{GIRL_NAME}, ты очень красивая ❤️",
        f"Я думаю о тебе 💭",
    ])


def generate_support():
    return f"{GIRL_NAME}, ты справляешься 💪"


def generate_med_joke():
    return random.choice([
        "😂 Медсестры не устают — они перезагружаются",
        "😂 Если тихо — значит сейчас будет весело",
    ])

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot online 💕",
        reply_markup=keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💌 Сейчас":
        await update.message.reply_text(generate_compliment())

    elif text == "🩺 После смены":
        await update.message.reply_text(generate_support())

    elif text == "😂 Шутка":
        await update.message.reply_text(generate_med_joke())

    else:
        await update.message.reply_text("💭")


# ================= WEB SERVER =================

async def health(request):
    return web.Response(text="OK")


async def telegram_webhook(request):
    data = await request.json()

    update = Update.de_json(data, request.app["bot"])

    await request.app["application"].process_update(update)

    return web.Response(text="OK")


async def run_web(app):
    web_app = web.Application()

    web_app["application"] = app
    web_app["bot"] = app.bot

    web_app.router.add_get("/", health)
    web_app.router.add_post(WEBHOOK_PATH, telegram_webhook)

    runner = web.AppRunner(web_app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("WEB SERVER STARTED")


# ================= MAIN =================

async def main():

    state = load_state()

    app = ApplicationBuilder().token(TOKEN).build()
    app.bot_data.update(state)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()

    # webhook URL
    webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"

    await app.bot.set_webhook(webhook_url)

    print("WEBHOOK SET:", webhook_url)

    await run_web(app)

    print("BOT IS RUNNING")

    # держим процесс живым
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

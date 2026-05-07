import random
import os
import asyncio
import json

from aiohttp import web

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===================== CONFIG =====================

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

GIRL_NAME = "Танюша"

AUTO_KEY = "auto_enabled"
TIRED_KEY = "user_tired"

STATE_FILE = "state.json"

auto_task = None

# ===================== STATE =====================

def save_state(data):
    try:
        safe_data = {
            AUTO_KEY: data.get(AUTO_KEY, False),
            TIRED_KEY: data.get(TIRED_KEY, False),
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(safe_data, f)
    except Exception as e:
        print("STATE SAVE ERROR:", e)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {AUTO_KEY: False, TIRED_KEY: False}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {AUTO_KEY: False, TIRED_KEY: False}

# ===================== KEYBOARD =====================

def keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💌 Сейчас")],
            [KeyboardButton("🩺 После смены")],
            [KeyboardButton("😂 Шутка")],
            [KeyboardButton("▶️ Авто"), KeyboardButton("⏸️ Стоп")],
        ],
        resize_keyboard=True
    )

# ===================== CONTENT =====================

def generate_med_joke():
    return random.choice([
        "😂 Медсестры уже не нервничают — они закалённые",
        "😂 Врач сказал отдыхать… ага, конечно",
        "😂 Если тихо — значит сейчас будет весело",
        "😂 Кофе не помогает? Значит ты настоящая медсестра",
        "😂 Мир держится на медсестрах",
    ])


def generate_special():
    return random.choice([
        f"{GIRL_NAME}, ты самая лучшая 💕",
        f"Как же мне так повезло с тобой, {GIRL_NAME}?",
        f"{GIRL_NAME}, you stole all my thoughts ❤️",
    ])


def generate_surprise():
    return random.choice([
        "💌 Ты сейчас очень красивая",
        "🌸 Ты чудо",
        "💖 Я сейчас подумал о тебе",
        generate_med_joke(),
    ])


def generate_nurse():
    return random.choice([
        f"{GIRL_NAME}, ты спасаешь людей ❤️",
        f"{GIRL_NAME}, ты настоящая героиня 🏥",
        f"{GIRL_NAME}, у тебя золотое сердце",
    ])


def generate_support():
    return random.choice([
        f"{GIRL_NAME}, ты устала… ты умничка 💖",
        f"{GIRL_NAME}, ты справляешься 💪",
        f"{GIRL_NAME}, отдыхай 🫶",
    ])


def generate_snack():
    return random.choice([
        "Сендвич с сыром и овощами",
        "🍫 Шоколадка для настроения",
        "🍌 Банан — энергия за пару минут",
        "Печенье и чай — уютно и вкусно",
    ])


def generate_compliment():
    r = random.random()

    if r < 0.15:
        return generate_support()
    if r < 0.30:
        return generate_nurse()
    if r < 0.45:
        return generate_med_joke()
    if r < 0.60:
        return generate_surprise()
    if r < 0.75:
        return generate_special()

    return (
        f"{GIRL_NAME}, ты невероятно красивая "
        f"и это невозможно не заметить ❤️"
    )

# ===================== SMART REPLY =====================

def smart_reply(text, tired):
    text = text.lower()

    if "устала" in text:
        return f"{GIRL_NAME}, иди ко мне… отдыхай 💖", True

    if "отдохнула" in text:
        return f"{GIRL_NAME}, вот и правильно 💖", False

    if "привет" in text:
        return f"Привет, {GIRL_NAME} 😍", tired

    if "люблю" in text:
        return "И я люблю тебя ❤️", tired

    if "скучаю" in text:
        return random.choice([
            f"Я тоже скучаю 💖",
            f"{GIRL_NAME}, я очень скучаю 😔❤️",
        ]), tired

    if "грустно" in text:
        return f"{GIRL_NAME}, я рядом 🤍", tired

    if "голодн" in text:
        return f"{GIRL_NAME}, {generate_snack()}", tired

    return None, tired

# ===================== AUTO MODE =====================

async def auto_send(bot, app):
    print("AUTO STARTED")

    while app.bot_data.get(AUTO_KEY, False):

        await asyncio.sleep(random.randint(7200, 18000))

        if not app.bot_data.get(AUTO_KEY, False):
            break

        text = random.choice([
            generate_compliment(),
            generate_special(),
            generate_surprise(),
            f"{GIRL_NAME}, думаю о тебе 💭",
        ])

        try:
            await bot.send_message(chat_id=CHAT_ID, text=text)
            print("AUTO:", text)
        except Exception as e:
            print("AUTO ERROR:", e)

    print("AUTO STOPPED")

# ===================== HANDLERS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.application.bot_data[AUTO_KEY] = False
    context.application.bot_data[TIRED_KEY] = False

    await update.message.reply_text(
        "Yes milk💕",
        reply_markup=keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    app_data = context.application.bot_data

    if text == "💌 Сейчас":
        await update.message.reply_text(generate_compliment())

    elif text == "🩺 После смены":
        await update.message.reply_text(
            generate_support() + "\n\n" + generate_nurse()
        )

    elif text == "😂 Шутка":
        await update.message.reply_text(generate_med_joke())

    elif text == "▶️ Авто":
        if not app_data.get(AUTO_KEY, False):
            app_data[AUTO_KEY] = True
            asyncio.create_task(auto_send(context.bot, context.application))

        await update.message.reply_text("Авто включено 💕")

    elif text == "⏸️ Стоп":
        app_data[AUTO_KEY] = False
        await update.message.reply_text("Авто выключено")

    else:
        reply, tired = smart_reply(text, app_data.get(TIRED_KEY, False))

        app_data[TIRED_KEY] = tired

        if reply:
            await update.message.reply_text(reply)

# ===================== WEB (Render ping) =====================

async def health(request):
    return web.Response(text="Bot is alive!")


async def run_web():
    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("WEB SERVER STARTED")

# ===================== MAIN =====================

async def main():

    state = load_state()

    app = ApplicationBuilder().token(TOKEN).build()
    app.bot_data.update(state)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await run_web()

    if app.bot_data.get(AUTO_KEY, False):
        asyncio.create_task(auto_send(app.bot, app))

    print("BOT STARTED")

    # ❗ ВАЖНО: правильный запуск PTB 20.7
    await app.run_polling()

# ===================== START =====================

if __name__ == "__main__":
    asyncio.run(main())

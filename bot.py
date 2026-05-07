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


TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("TOKEN или CHAT_ID не заданы")

CHAT_ID = int(CHAT_ID)

GIRL_NAME = "Танюша"

AUTO_KEY = "auto_enabled"
TIRED_KEY = "user_tired"

STATE_FILE = "state.json"

auto_task = None




def save_state(data):
    safe_data = {
        AUTO_KEY: data.get(AUTO_KEY, False),
        TIRED_KEY: data.get(TIRED_KEY, False),
    }

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(safe_data, f)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {AUTO_KEY: False, TIRED_KEY: False}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {AUTO_KEY: False, TIRED_KEY: False}



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




def generate_med_joke():
    return random.choice([
        "😂 Медсестры уже не нервничают",
        "😂 Врач сказал отдыхать… ага конечно",
        "😂 Если тихо — значит будет весело",
        "😂 Кофе не помогает? значит ты медсестра",
        "😂 Мир держится на медсестрах",
    ])


def generate_special():
    return random.choice([
        f"{GIRL_NAME}, ты самая лучшая 💕",
        f"Как же мне повезло с тобой, {GIRL_NAME}?",
        f"{GIRL_NAME}, ты украла мои мысли ❤️",
    ])


def generate_surprise():
    return random.choice([
        "💌 Ты сейчас очень красивая",
        "🌸 Ты чудо",
        "💖 Я думаю о тебе",
        generate_med_joke(),
    ])


def generate_nurse():
    return random.choice([
        f"{GIRL_NAME}, ты спасаешь людей ❤️",
        f"{GIRL_NAME}, ты героиня 🏥",
        f"{GIRL_NAME}, у тебя золотое сердце",
    ])


def generate_support():
    return random.choice([
        f"{GIRL_NAME}, ты устала… отдыхай 💖",
        f"{GIRL_NAME}, ты справляешься 💪",
        f"{GIRL_NAME}, я рядом 🫶",
    ])


def generate_snack():
    return random.choice([
        "🍫 шоколадка",
        "🍌 банан",
        "🥪 сендвич",
        "🍎 яблоко",
        "🍵 чай",
    ])


def generate_compliment():
    r = random.random()

    if r < 0.12:
        return generate_support()
    elif r < 0.24:
        return generate_nurse()
    elif r < 0.36:
        return generate_med_joke()
    elif r < 0.52:
        return generate_surprise()
    elif r < 0.72:
        return generate_special()

    return f"{GIRL_NAME}, ты невероятно красивая 💖"




def smart_reply(text, tired):
    text = text.lower()

    if "устала" in text:
        return f"{GIRL_NAME}, иди ко мне 💖", True

    if "привет" in text:
        return f"Привет, {GIRL_NAME} 😍", tired

    if "люблю" in text:
        return "И я тебя ❤️", tired

    if "скучаю" in text:
        return f"{GIRL_NAME}, я тоже скучаю 💕", tired

    if "голодн" in text:
        return f"{GIRL_NAME}, перекус: {generate_snack()}", tired

    return None, tired




async def auto_send(app):
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
            await app.bot.send_message(chat_id=CHAT_ID, text=text)
            print("AUTO:", text)
        except Exception as e:
            print("AUTO ERROR:", e)

    print("AUTO STOPPED")




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yes milk💕", reply_markup=keyboard())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global auto_task

    text = update.message.text
    data = context.application.bot_data

    if text == "💌 Сейчас":
        await update.message.reply_text(generate_compliment())

    elif text == "🩺 После смены":
        await update.message.reply_text(generate_support() + "\n\n" + generate_nurse())

    elif text == "😂 Шутка":
        await update.message.reply_text(generate_med_joke())

    elif text == "▶️ Авто":

        if not data.get(AUTO_KEY, False):
            data[AUTO_KEY] = True
            save_state(data)

            if auto_task is None or auto_task.done():
                auto_task = asyncio.create_task(auto_send(context.application))

        await update.message.reply_text("Авто включено 💕")

    elif text == "⏸️ Стоп":
        data[AUTO_KEY] = False
        save_state(data)
        await update.message.reply_text("Авто выключено")

    else:
        reply, tired = smart_reply(text, data.get(TIRED_KEY, False))
        data[TIRED_KEY] = tired
        save_state(data)

        if reply:
            await update.message.reply_text(reply)



async def health(request):
    return web.Response(text="Bot is alive!")


async def run_web_server():
    app_web = web.Application()
    app_web.router.add_get("/", health)

    runner = web.AppRunner(app_web)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print("WEB SERVER STARTED")




async def main():

    global auto_task

    state = load_state()

    app = ApplicationBuilder().token(TOKEN).build()

    app.bot_data.update(state)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await run_web_server()

    await app.initialize()
    await app.start()

    print("BOT STARTED")

    if app.bot_data.get(AUTO_KEY, False):
        auto_task = asyncio.create_task(auto_send(app))

    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

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
CHAT_ID = int(os.getenv("CHAT_ID"))

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
        return {
            AUTO_KEY: False,
            TIRED_KEY: False,
        }

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except:
        return {
            AUTO_KEY: False,
            TIRED_KEY: False,
        }



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
        "😂 Медсестры уже не нервничают — они закалённые",
        "😂 Врач сказал отдыхать… ага, конечно",
        "😂 Если тихо — значит сейчас будет весело",
        "😂 Кофе не помогает? Значит ты настоящая медсестра",
        "😂 Мир держится на медсестрах",
        "😂 Пациент сказал “болит живот”, я сказала “болит ваша фантазия”.",
        "😂 Кофе в одной руке, шприц в другой — супергеройский стиль!",
        "😂 Если пациент боится укола, я боюсь его отменить — скучно же!",
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
    snacks = [
        "Сендвич с сыром и овощами",
        "Яблоко или груша — быстрый перекус",
        "🍫 Шоколадка для настроения",
        "🍌 Банан — энергия за пару минут",
        "Салат с курицей или тунцом",
        "Печенье и чай — уютно и вкусно",
    ]

    return random.choice(snacks)


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

    starts = [
        f"{GIRL_NAME}, ты",
        f"{GIRL_NAME}, знаешь, ты",
        f"{GIRL_NAME}, честно — ты",
        f"{GIRL_NAME}, мне кажется, ты",
        f"{GIRL_NAME}, иногда я думаю, что ты",
        f"{GIRL_NAME}, ты просто",
    ]

    adjectives = [
        "невероятно красивая",
        "очень милая",
        "просто волшебная",
        "безумно притягательная",
        "очень особенная",
        "такая нежная",
        "невероятно добрая",
        "очень уютная",
        "необыкновенная",
    ]

    endings = [
        "и это невозможно не заметить ❤️",
        "и от тебя невозможно оторвать взгляд",
        "и ты делаешь мир лучше",
        "и рядом с тобой спокойно",
        "и ты сводишь меня с ума 💖",
        "и это чувствуется сразу",
        "и это просто факт",
    ]

    extras = [
        "",
        " Правда.",
        " И я не шучу.",
        " Это уже невозможно игнорировать.",
        " Каждый раз убеждаюсь в этом.",
    ]

    emojis = ["❤️", "💖", "😍", "🥰", "✨"]

    return (
        f"{random.choice(starts)} "
        f"{random.choice(adjectives)}, "
        f"{random.choice(endings)}"
        f"{random.choice(extras)} "
        f"{random.choice(emojis)}"
    )



def smart_reply(text, tired):

    text = text.lower()

    if "устала" in text:
        return f"{GIRL_NAME}, иди ко мне… ты заслужила отдых 💖", True

    if "отдохнула" in text:
        return f"{GIRL_NAME}, вот и правильно 💖", False

    if "привет" in text:
        return f"Привет, {GIRL_NAME} 😍", tired

    if "люблю" in text:
        return "И я люблю тебя ❤️", tired

    if "скучаю" in text:
        return random.choice([
            f"Я тоже скучаю по тебе, {GIRL_NAME} 💖",
            f"{GIRL_NAME}, я очень скучаю 😔❤️",
            "Скучаешь? Иди ко мне 💕",
        ]), tired

    if "грустно" in text or "плохо" in text:
        return f"{GIRL_NAME}, я рядом 🤍", tired

    if "голодн" in text:
        return (
            f"{GIRL_NAME}, давай что-нибудь вкусненькое 🍴 "
            f"{generate_snack()}"
        ), tired

    if tired and random.random() < 0.25:
        return f"{GIRL_NAME}, ты как сейчас? 💭", tired

    if random.random() < 0.10:
        return random.choice([
            f"{GIRL_NAME}, думаю о тебе 💭",
            "Ты сейчас очень красивая ❤️",
        ]), tired

    return None, tired



async def auto_send(bot, app):

    print("AUTO MODE STARTED")

    while app.bot_data.get(AUTO_KEY, False):

        # 2 - 5 часов
        delay = random.randint(7200, 18000)

        await asyncio.sleep(delay)

        if not app.bot_data.get(AUTO_KEY, False):
            break

        options = [
            generate_compliment(),
            generate_compliment(),
            generate_compliment(),
            generate_special(),
            generate_surprise(),
            f"{GIRL_NAME}, думаю о тебе 💭",
        ]

        text = random.choice(options)

        try:

            await bot.send_message(
                chat_id=CHAT_ID,
                text=text
            )

            print("AUTO:", text)

        except Exception as e:
            print("AUTO ERROR:", e)

    print("AUTO MODE STOPPED")



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Yes milk💕",
        reply_markup=keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global auto_task

    text = update.message.text

    app_data = context.application.bot_data

    if text == "💌 Сейчас":

        await update.message.reply_text(
            generate_compliment()
        )

    elif text == "🩺 После смены":

        await update.message.reply_text(
            generate_support() +
            "\n\n" +
            generate_nurse()
        )

    elif text == "😂 Шутка":

        await update.message.reply_text(
            generate_med_joke()
        )

    elif text == "▶️ Авто":

        if not app_data.get(AUTO_KEY, False):

            app_data[AUTO_KEY] = True

            save_state(app_data)

            if auto_task is None or auto_task.done():

                auto_task = asyncio.create_task(
                    auto_send(
                        context.bot,
                        context.application
                    )
                )

        await update.message.reply_text(
            "Авто включено 💕"
        )

    elif text == "⏸️ Стоп":

        app_data[AUTO_KEY] = False

        save_state(app_data)

        await update.message.reply_text(
            "Авто выключено"
        )

    else:

        reply, tired = smart_reply(
            text,
            app_data.get(TIRED_KEY, False)
        )

        app_data[TIRED_KEY] = tired

        save_state(app_data)

        if reply:
            await update.message.reply_text(reply)



async def health(request):
    return web.Response(text="Bot is alive!")

async def run_web_server():

    web_app = web.Application()

    web_app.router.add_get("/", health)

    runner = web.AppRunner(web_app)

    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print("WEB SERVER STARTED")


async def main():

    global auto_task

    state = load_state()

    app = ApplicationBuilder().token(TOKEN).build()

    app.bot_data.update(state)

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    await run_web_server()

    await app.initialize()

    await app.start()

    await app.updater.start_polling()

    print("BOT STARTED")


    if app.bot_data.get(AUTO_KEY, False):

        auto_task = asyncio.create_task(
            auto_send(app.bot, app)
        )

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

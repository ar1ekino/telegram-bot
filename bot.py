import random
import os
from datetime import time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
GIRL_NAME = "Таня"

auto_enabled = False


def keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💌 Сейчас")],
            [KeyboardButton("▶️ Авто"), KeyboardButton("⏸️ Стоп")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def generate_special():
    specials = [
        f"{GIRL_NAME}, я просто напомню: ты лучшая 💕",
        f"Иногда я думаю... как мне так повезло с тобой, {GIRL_NAME}? 😍",
        f"{GIRL_NAME}, ты сегодня украла все мои мысли ❤️",
        f"Я не знаю как, но ты каждый день становишься ещё красивее",
    ]
    return random.choice(specials)


def generate_compliment():
    if random.random() < 0.2:  # 20% шанс на специальный комплимент
        return generate_special()

    starts = [
        f"{GIRL_NAME}, ты",
        f"{GIRL_NAME}, знаешь, ты",
        f"{GIRL_NAME}, мне кажется, ты",
        f"{GIRL_NAME}, честно — ты",
    ]

    adjectives = [
        "невероятно красивая",
        "очень милая",
        "просто волшебная",
        "безумно притягательная",
        "очень особенная",
        "такая нежная",
        "очень тёплая",
        "просто идеальная",
    ]

    endings = [
        "и это невозможно не заметить ❤️",
        "и от тебя невозможно оторвать взгляд 😍",
        "и ты делаешь этот мир лучше",
        "и рядом с тобой спокойно",
        "и ты сводишь меня с ума 💖",
        "и это правда",
        "и это чувствуется сразу",
    ]

    extra = [
        "",
        " Ты даже не представляешь насколько.",
        " Серьёзно.",
        " Каждый раз убеждаюсь в этом.",
        " Это не комплимент — это факт.",
    ]

    return f"{random.choice(starts)} {random.choice(adjectives)}, {random.choice(endings)}{random.choice(extra)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я тут 💕", reply_markup=keyboard())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_enabled
    text = update.message.text

    if text == "💌 Сейчас":
        await update.message.reply_text(generate_compliment())

    elif text == "▶️ Авто":
        auto_enabled = True
        schedule(context)
        await update.message.reply_text("Авто включено 💕")

    elif text == "⏸️ Стоп":
        auto_enabled = False
        context.job_queue.jobs().clear()
        await update.message.reply_text("Авто выключено")


def schedule(context):
    if auto_enabled:
        delay = random.randint(7200, 15000)  # 2–4 часа
        context.job_queue.run_once(send_msg, delay)

async def send_msg(context: ContextTypes.DEFAULT_TYPE):
    if auto_enabled:
        await context.bot.send_message(chat_id=CHAT_ID, text=generate_compliment())
        schedule(context)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()

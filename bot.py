import random
import os
from datetime import time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, JobQueue


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


def generate_surprise():
    surprises = [
        f"🎁 Сюрприз! {GIRL_NAME}, помни, ты сегодня лучшая 😍",
        f"😂 Шутка дня: Почему кошка не работает на компьютере? Потому что боится мыши!",
        f"💌 Милый факт: {GIRL_NAME}, твоя улыбка может осветить целый день",
        f"🌸 Просто так: {GIRL_NAME}, ты чудо!",
        f"🐶 Представь: щенок рад тебя видеть так же, как я 🥰",
        f"🖼️ Стикер-вдохновение: 😘💖✨"
    ]
    return random.choice(surprises)


def generate_compliment():
    
    if random.random() < 0.15:
        return generate_surprise()
    
    if random.random() < 0.2:
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


async def morning_message(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"Доброе утро, {GIRL_NAME} 💖\n{generate_compliment()}"
    )

async def night_message(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"Спокойной ночи, {GIRL_NAME} 🌙\n{generate_compliment()}"
    )


app = ApplicationBuilder().token(TOKEN).build()


app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


job_queue = app.job_queue
job_queue.run_daily(morning_message, time(hour=8, minute=0))  # 8:00 утра
job_queue.run_daily(night_message, time(hour=22, minute=0))   # 22:00 вечера


app.run_polling()

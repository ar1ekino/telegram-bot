import random
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
GIRL_NAME = "Таня"

auto_enabled = False

import random

starts = [
    f"{GIRL_NAME}, ты",
    f"{GIRL_NAME}, ты сегодня",
    f"{GIRL_NAME}, знаешь, ты",
    f"{GIRL_NAME}, мне кажется, ты",
]

adjectives = [
    "невероятная",
    "очаровательная",
    "самая красивая",
    "волшебная",
    "потрясающая",
    "безумно милая",
]

endings = [
    "как всегда ❤️",
    "сегодня особенно 😍",
    "просто космос 💫",
    "и я от тебя в восторге",
    "и я не могу налюбоваться",
]

funny = [
    f"{GIRL_NAME}, ты как Wi-Fi — без тебя ничего не работает 😄",
    f"{GIRL_NAME}, ты красивее, чем мой код после фиксов",
    f"{GIRL_NAME}, ты — моя любимая зависимость ❤️",
]

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💌 Сейчас", callback_data="now")],
        [InlineKeyboardButton("▶️ Авто", callback_data="auto_on")],
        [InlineKeyboardButton("⏸️ Стоп", callback_data="auto_off")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я тут 💕", reply_markup=keyboard())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_enabled
    query = update.callback_query
    await query.answer()

    if query.data == "now":
        await query.message.reply_text(random.choice(compliments))

    elif query.data == "auto_on":
        auto_enabled = True
        schedule(context)
        await query.message.reply_text("Авто включено 💕")

    elif query.data == "auto_off":
        auto_enabled = False
        context.job_queue.jobs().clear()
        await query.message.reply_text("Авто выключено")

def schedule(context):
    if auto_enabled:
        delay = random.randint(7200, 15000)
        context.job_queue.run_once(send_msg, delay)

async def send_msg(context: ContextTypes.DEFAULT_TYPE):
    if auto_enabled:
        await context.bot.send_message(chat_id=CHAT_ID, text=random.choice(compliments))
        schedule(context)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

app.run_polling()

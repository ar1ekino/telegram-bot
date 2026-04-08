import random
import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters


TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
GIRL_NAME = "Танюша"

auto_enabled = False
user_state = {"tired": False}


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
        "😂 Медсестры уже не нервничают — они закалённые ",
        "😂 Врач сказал отдыхать… ага, конечно ",
        "😂 Если тихо — значит сейчас будет весело ",
        "😂 Кофе не помогает? Значит ты настоящая медсестра ",
        "😂 Мир держится на медсестрах ",
        "😂 Пациент сказал “болит живот”, я сказала “болит ваша фантазия”.",
        "😂 Кофе в одной руке, шприц в другой — супергеройский стиль! ",
        "😂 Если пациент боится укола, я боюсь его отменить — скучно же!",
        "😂Главная цель медсестры: чтобы пациенты выжили… а врачи не заметили, что мы всё исправили сами.",
    ])

def generate_special():
    return random.choice([
        f"{GIRL_NAME}, ты лучшая 💕",
        f"Как мне так повезло с тобой, {GIRL_NAME}? ",
        f"{GIRL_NAME}, ты украла все мои мысли ❤️",
    ])

def generate_surprise():
    return random.choice([
        f"🎁 Сюрприз! Ты сегодня особенно прекрасна ",
        f"💌 Твоя улыбка лечит лучше лекарств",
        f"🌸 Ты чудо",
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
    if r < 0.10: return generate_support()
    elif r < 0.20: return generate_nurse()
    elif r < 0.30: return generate_med_joke()
    elif r < 0.45: return generate_surprise()
    elif r < 0.65: return generate_special()

    starts = [
        f"{GIRL_NAME}, ты", f"{GIRL_NAME}, знаешь, ты",
        f"{GIRL_NAME}, честно — ты", f"{GIRL_NAME}, я понял одну вещь — ты",
        f"{GIRL_NAME}, мне кажется, ты", f"{GIRL_NAME}, иногда я думаю, что ты",
        f"{GIRL_NAME}, ты просто",
    ]
    adjectives = [
        "невероятно красивая", "очень милая", "просто волшебная",
        "безумно притягательная", "очень особенная", "такая нежная",
        "очень тёплая", "невероятно добрая", "очень уютная",
        "какая-то нереальная", "необыкновенная", "очень ласковая",
    ]
    endings = [
        "и это невозможно не заметить ❤️", "и от тебя невозможно оторвать взгляд ",
        "и ты делаешь мир лучше", "и рядом с тобой спокойно",
        "и ты сводишь меня с ума 💖", "и это чувствуется сразу",
        "и это просто факт", "и это видно в каждом твоём движении",
        "и это цепляет сильнее всего", "и это делает тебя особенной",
    ]
    extras = [
        "", " Ты даже не представляешь насколько.", " Правда.",
        " Каждый раз убеждаюсь в этом.", " Это не комплимент — это факт.",
        " И я не шучу.", " С каждым днём всё больше.", " Это уже невозможно игнорировать.",
    ]
    emojis = ["❤️", "💖", "😍", "🥰", "✨", "💫"]

    if random.random() < 0.1:
        return random.choice([f"{GIRL_NAME}, ты лучшая ❤️", f"Я сейчас подумал о тебе 💭", f"Ты очень красивая "])

    return f"{random.choice(starts)} {random.choice(adjectives)}, {random.choice(endings)}{random.choice(extras)} {random.choice(emojis)}"


def smart_reply(text):
    text = text.lower()
    if "устала" in text:
        user_state["tired"] = True
        return f"{GIRL_NAME}, иди ко мне… ты заслужила отдых 💖"
    if "отдохнула" in text:
        user_state["tired"] = False
        return f"{GIRL_NAME}, вот и правильно 💖"
    if "привет" in text:
        return f"Привет, {GIRL_NAME} 😍"
    if "люблю" in text:
        return f"Я тебя ещё сильнее ❤️"
    if "грустно" in text or "плохо" in text:
        return f"{GIRL_NAME}, я рядом 🤍"
    if "голодн" in text:
        return f"{GIRL_NAME}, давай что-нибудь вкусненькое  Я бы предложил: {generate_snack()}"
    if user_state["tired"] and random.random() < 0.3:
        return f"{GIRL_NAME}, ты как сейчас? 💭"
    if random.random() < 0.15:
        return random.choice([f"{GIRL_NAME}, думаю о тебе 💭", "Ты сейчас очень красивая"])
    return None


async def follow_up(context):
    await asyncio.sleep(random.randint(600, 1800))  
    if user_state["tired"]:
        await context.bot.send_message(chat_id=CHAT_ID, text=f"{GIRL_NAME}, как ты? 💖")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я тут 💕", reply_markup=keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_enabled
    text = update.message.text

    if text == "💌 Сейчас":
        await update.message.reply_text(generate_compliment())
    elif text == "🩺 После смены":
        await update.message.reply_text(generate_support() + "\n\n" + generate_nurse())
    elif text == "😂 Шутка":
        await update.message.reply_text(generate_med_joke())
    elif text == "▶️ Авто":
        if not auto_enabled:
            auto_enabled = True
            context.application.create_task(auto_send(context))  
        await update.message.reply_text("Авто включено 💕")
    elif text == "⏸️ Стоп":
        auto_enabled = False
        await update.message.reply_text("Авто выключено")
    else:
        reply = smart_reply(text)
        if reply:
            await update.message.reply_text(reply)
            if user_state["tired"]:
                context.application.create_task(follow_up(context))  


async def auto_send(context):
    global auto_enabled
    while auto_enabled:
        await asyncio.sleep(random.randint(72, 75))  
        if not auto_enabled:
            break
        if random.random() < 0.3:
            text = random.choice([f"{GIRL_NAME}, думаю о тебе 💭", "Как ты там? 🫶"])
        else:
            text = generate_compliment()
        await context.bot.send_message(chat_id=CHAT_ID, text=text)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()

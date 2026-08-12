import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# --- 1. НАСТРОЙКА ---
TELEGRAM_TOKEN = "8852265249:AAHj__vj7QVvotqj9kmZr7qmRUJ3jycmuJA"
GEMINI_API_KEY = "AQ.Ab8RN6LQNNO3kbD9PWT0yUxeg3PEMKmpUsPI1aKFw1jnTToUag"
BOT_NAME = "Veagline AI"

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
# Используем gemini-3.1-flash-lite — лёгкая и быстрая модель
model = genai.GenerativeModel('gemini-3.1-flash-lite')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Хранилище истории диалогов
user_sessions = {}

def get_chat(chat_id):
    if chat_id not in user_sessions:
        user_sessions[chat_id] = model.start_chat(history=[])
    return user_sessions[chat_id]

# --- 2. ОБРАБОТЧИКИ КОМАНД ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Привет! Я {BOT_NAME}, твой ИИ-помощник на базе Google Gemini. 🚀\n"
        "Просто напиши мне что-нибудь, и я отвечу."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        chat = get_chat(chat_id)
        response = chat.send_message(user_message)
        reply_text = response.text

        if len(reply_text) > 4096:
            for x in range(0, len(reply_text), 4096):
                await update.message.reply_text(reply_text[x:x+4096])
        else:
            await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Ошибка при обращении к Gemini: {e}")
        await update.message.reply_text("😅 Произошла ошибка при обработке запроса. Попробуй позже.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in user_sessions:
        del user_sessions[chat_id]
    await update.message.reply_text("История нашего диалога очищена. Начинаем с чистого листа! 🧹")

# --- 3. ЗАПУСК БОТА ---

if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"🤖 Бот {BOT_NAME} запущен и готов к работе...")
    application.run_polling()
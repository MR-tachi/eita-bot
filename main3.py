import sqlite3
import json
import telebot
from telebot.types import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telebot.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
MAX_ATTEMPTS=3
TOKEN = "7665262106:AAHqal2VNOQUgCLBTMwWESPglCRER_6bIQ"
CHANNEL_LINK = "https://t.me/+TMV2MI-C8JhjYjlk"

PERSONNEL_CODE, QUESTION = range(2)

def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valid_codes (
            code TEXT PRIMARY KEY
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO valid_codes (code) VALUES ('1012'), ('1013')")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            personnel_code TEXT,
            answers TEXT,
            submitted INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def is_valid_code(code):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM valid_codes WHERE code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_questions():
    return [
        "سوال 1: نام کامل خود را وارد کنید.",
        "سوال 2: شغل شما چیست؟"
    ]

def insert_user(telegram_id, personnel_code, answers):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT answers FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()

    if result:
        new_answers = result[0] + " | " + answers
        cursor.execute("UPDATE users SET answers = ? WHERE telegram_id = ?", (new_answers, telegram_id))
    else:
        cursor.execute("""
            INSERT INTO users (telegram_id, personnel_code, answers, submitted)
            VALUES (?, ?, ?, 0)
        """, (telegram_id, personnel_code, answers))

    conn.commit()
    conn.close()

def mark_as_submitted(telegram_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET submitted = 1 WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext):
    context.user_data['attempts'] = 0
    update.message.reply_text("سلام! لطفاً کد پرسنلی خود را وارد کنید.")
    return PERSONNEL_CODE

def personnel_code(update: Update, context: CallbackContext):
    code = update.message.text
    context.user_data['attempts'] += 1
    if is_valid_code(code):
        update.message.reply_text("✅ کد پرسنلی معتبر است. حالا فرم را تکمیل کنید.")
        context.user_data['personnel_code'] = code
        context.user_data['answers'] = []
        context.user_data['question_index'] = 0
        return ask_question(update, context)
    else:
        if context.user_data['attempts'] < MAX_ATTEMPTS:
            update.message.reply_text("❌ کد پرسنلی نامعتبر است. لطفاً مجدداً تلاش کنید.")
            return PERSONNEL_CODE
        else:
            update.message.reply_text("⛔️ شما دو بار کد اشتباه وارد کردید. مکالمه پایان یافت.")
            return ConversationHandler.END

def ask_question(update: Update, context: CallbackContext):
    questions = get_questions()
    index = context.user_data['question_index']

    if index < len(questions):
        update.message.reply_text(questions[index])
        return QUESTION
    else:
        return complete_form(update, context)

def question(update: Update, context: CallbackContext):
    answer = update.message.text
    context.user_data['answers'].append(answer)
    context.user_data['question_index'] += 1
    return ask_question(update, context)

def complete_form(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    personnel_code = context.user_data['personnel_code']
    answers = " | ".join(context.user_data['answers'])

    insert_user(telegram_id, personnel_code, answers)
    mark_as_submitted(telegram_id)

    update.message.reply_text("✅ فرم شما تکمیل شد. این هم لینک کانال:")
    update.message.reply_text("📢 [لینک کانال شما](https://t.me/yourchannel)", parse_mode="Markdown")

    return ConversationHandler.END

def leave_channel(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        context.bot.send_message(chat_id=context.bot.get_me().id, text=f"⚠️ کاربر {telegram_id} از کانال خارج شد.")
    
    conn.close()

def main():
    create_db()

    application = Application.builder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PERSONNEL_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, personnel_code)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question)],
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, leave_channel))

    application.run_polling()

if __name__ == '__main__':
    main()

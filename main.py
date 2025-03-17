import sqlite3
import json
import balebot
from balebot.handlers import MessageHandler, CommandHandler, ConversationHandler
from balebot.models.messages import TextMessage
from balebot.models.base_models import Peer
from balebot.utils.logger import Logger
from balebot.updater import Updater

TOKEN = "486382545:cAMgaei7WeXx6HXE1A43ms9VXA6y9QTlkhJV7M41"  # توکن ربات بله را اینجا قرار دهید
CHANNEL_LINK = "ble.ir/join/BE9oQHxKhW"
MANAGER_CHAT_ID = 123456789
MAX_ATTEMPTS = 2
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

async def start(bot, update):
    user_peer = update.get_effective_user()
    message = TextMessage("سلام! لطفاً کد پرسنلی خود را وارد کنید.")
    await bot.send_message(message, user_peer)
    return PERSONNEL_CODE

async def personnel_code(bot, update):
    user_peer = update.get_effective_user()
    code = update.get_effective_message().text
    user_id = user_peer.peer_id
    
    if 'attempts' not in bot.user_data:
        bot.user_data['attempts'] = 0
    bot.user_data['attempts'] += 1

    if is_valid_code(code):
        message = TextMessage("✅ کد پرسنلی معتبر است. حالا فرم را تکمیل کنید.")
        await bot.send_message(message, user_peer)
        bot.user_data['personnel_code'] = code
        bot.user_data['answers'] = []
        bot.user_data['question_index'] = 0
        return await ask_question(bot, update)
    else:
        if bot.user_data['attempts'] < MAX_ATTEMPTS:
            message = TextMessage("❌ کد پرسنلی نامعتبر است. لطفاً مجدداً تلاش کنید.")
            await bot.send_message(message, user_peer)
            return PERSONNEL_CODE
        else:
            message = TextMessage("⛔️ شما دو بار کد اشتباه وارد کردید. مکالمه پایان یافت.")
            await bot.send_message(message, user_peer)
            return ConversationHandler.END

async def ask_question(bot, update):
    user_peer = update.get_effective_user()
    questions = get_questions()
    index = bot.user_data['question_index']

    if index < len(questions):
        message = TextMessage(questions[index])
        await bot.send_message(message, user_peer)
        return QUESTION
    else:
        return await complete_form(bot, update)

async def question(bot, update):
    answer = update.get_effective_message().text
    bot.user_data['answers'].append(answer)
    bot.user_data['question_index'] += 1
    return await ask_question(bot, update)

async def complete_form(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    personnel_code = bot.user_data['personnel_code']
    answers = " | ".join(bot.user_data['answers'])
    
    insert_user(user_id, personnel_code, answers)
    mark_as_submitted(user_id)
    
    message1 = TextMessage("✅ فرم شما تکمیل شد. این هم لینک کانال:")
    message2 = TextMessage(CHANNEL_LINK)
    
    await bot.send_message(message1, user_peer)
    await bot.send_message(message2, user_peer)
    
    return ConversationHandler.END

async def leave_channel(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        cursor.execute("DELETE FROM users WHERE telegram_id = ?", (user_id,))
        conn.commit()
        
        # Send message to manager
        manager_peer = Peer(peer_id=MANAGER_CHAT_ID)
        message = TextMessage(f"⚠️ کاربر {user_id} از کانال خارج شد.")
        await bot.send_message(message, manager_peer)
    
    conn.close()

def main():
    create_db()
    
    updater = Updater(token=TOKEN, base_url="https://tapi.bale.ai/")
    
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PERSONNEL_CODE: [MessageHandler(TextMessage(), personnel_code)],
            QUESTION: [MessageHandler(TextMessage(), question)],
        },
        fallbacks=[]
    )

    updater.dispatcher.add_handler(conversation_handler)
    updater.dispatcher.add_handler(MessageHandler(TextMessage, leave_channel))
    
    updater.run()

if __name__ == '__main__':
    main()        

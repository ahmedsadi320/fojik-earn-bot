import sqlite3
import logging
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ১. ফ্ল্যাস্ক (Flask) সেটআপ (রেন্ডারকে জাগিয়ে রাখার জন্য)
server = Flask(__name__)

@server.route('/')
def hello():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    server.run(host='0.0.0.0', port=port)

# ২. ডাটাবেস ফাংশন
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [u[0] for u in c.fetchall()]
    conn.close()
    return users

# ৩. কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    first_name = update.effective_user.first_name
    text = f"✅ স্বাগতম {first_name}!\n🎁 আপনি পেয়েছেন 50 পয়েন্ট বোনাস!"
    keyboard = [[InlineKeyboardButton("👉 ইনকাম শুরু করুন", url="https://t.me/your_link")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = 7482645491
    if update.effective_user.id != ADMIN_ID: return
    if update.message.reply_to_message:
        target_msg = update.message.reply_to_message
        users = get_all_users()
        success = 0
        for user_id in users:
            try:
                await context.bot.copy_message(chat_id=user_id, from_chat_id=update.effective_chat.id, message_id=target_msg.message_id)
                success += 1
            except: continue
        await update.message.reply_text(f"✅ {success} জনকে পাঠানো হয়েছে।")
    else:
        await update.message.reply_text("⚠️ মেসেজটি Reply দিয়ে কমান্ড লিখুন।")

# ৪. মেইন রানার
if __name__ == '__main__':
    init_db()
    
    # ফ্ল্যাস্ককে আলাদা থ্রেডে রান করা (যাতে বট এবং ওয়েব পোর্ট দুইটাই একসাথে চলে)
    threading.Thread(target=run_flask).start()
    
    # আপনার বট টোকেন দিন
    TOKEN = "8584041971:AAGo2IcR2rE7mVWFUIXEh8F10Ld0jSMok-I" 
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    print("Bot and Server are starting...")
    app.run_polling()

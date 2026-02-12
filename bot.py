import sqlite3
import logging
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ১. ফ্ল্যাস্ক (Flask) সেটআপ (রেন্ডারকে সচল রাখার জন্য)
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

# ৩. কমান্ড হ্যান্ডলার (আপনার স্ক্রিনশটের স্টাইল অনুযায়ী)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    
    first_name = update.effective_user.first_name
    text = (f"𝐇𝐞𝐥𝐥𝐨 ❝{first_name}❞\n"
            "প্রিয় বন্ধু...🥰\n"
            "আমাদের ❝𝐅𝐨𝐣𝐢𝐤 𝐄𝐚𝐫𝐧❞ প্লাটফর্ম'টিতে যুক্ত হওয়ার জন্য আপনাকে ধন্যবাদ!🥰\n\n"
            "💸এখানে আপনি প্রতিদিন বিজ্ঞাপন(Ads) দেখে আয় করতে পারবেন।এবং আপনার বন্ধুকে আমন্ত্রণ জানিয়ে আয় করতে পারবেন।✅\n\n"
            "✉️যেকোনো প্রয়োজনে 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐓𝐞𝐚𝐦 এর সাথে যোগাযোগ করুন।\n"
            "🎬কিভাবে আয় করবেন 𝗧𝘂𝘁𝗼𝗿𝗶𝗮𝗹 ভিডিও দেখে শিখে নিতে পারেন।\n\n"
            "﻿♻️নিচের 𝗢𝗽𝗲𝗻 𝗡𝗼𝘄 এ ক্লিক করে,সহজেই আয় করা শুরু করুন!\n"
            "❝ধন্যবাদ❞🥰")
    
    keyboard = [
        [InlineKeyboardButton("✅𝗢𝗽𝗲𝗻 𝗡𝗼𝘄✅", url="https://t.me/your_link")],
        [InlineKeyboardButton("✅𝗢𝗽𝗲𝗻 𝗧𝘂𝘁𝗼𝗿𝗶𝗮𝗹✅", url="https://youtube.com/your_video")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = 7482645491
    if update.effective_user.id != ADMIN_ID: return

    if update.message.reply_to_message:
        target_msg = update.message.reply_to_message
        users = get_all_users()
        
        # বাটন এবং লিঙ্ক আলাদা করা (বিকল্প)
        cmd_text = update.message.text.replace('/broadcast', '').strip()
        custom_markup = None
        
        if "|" in cmd_text:
            try:
                btn_name, btn_url = cmd_text.split("|")
                keyboard = [[InlineKeyboardButton(btn_name.strip(), url=btn_url.strip())]]
                custom_markup = InlineKeyboardMarkup(keyboard)
            except:
                await update.message.reply_text("❌ ফরম্যাট: /broadcast বাটন নাম | লিঙ্ক")
                return

        success = 0
        for user_id in users:
            try:
                await context.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=update.effective_chat.id,
                    message_id=target_msg.message_id,
                    reply_markup=custom_markup
                )
                success += 1
            except: continue
        await update.message.reply_text(f"✅ {success} জন ইউজারকে ব্রডকাস্ট পাঠানো হয়েছে।")
    else:
        await update.message.reply_text("⚠️ নিয়ম: মেসেজটি Reply দিয়ে কমান্ড লিখুন।")

# ৪. মেইন রানার
if __name__ == '__main__':
    init_db()
    # ফ্ল্যাস্ক রান করা
    threading.Thread(target=run_flask).start()
    
    TOKEN = "8584041971:AAGo2IcR2rE7mVWFUIXEh8F10Ld0jSMok-I" 
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    print("Bot and Server are starting...")
    app.run_polling()

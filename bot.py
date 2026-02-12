import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ১. ডাটাবেস সেটআপ (ইউজার আইডি সেভ করার জন্য)
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

# ২. /start কমান্ডের জন্য ডিফল্ট বাটন
def start_buttons():
    keyboard = [
        [InlineKeyboardButton("👉 ইনকাম শুরু করুন", url="https://t.me/your_link")],
        [InlineKeyboardButton("🎬 টিউটোরিয়াল ভিডিও", url="https://youtube.com/your_video")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ৩. কমান্ড হ্যান্ডলার ফাংশনসমূহ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id) # ইউজারের আইডি ডাটাবেসে সেভ হবে
    
    first_name = update.effective_user.first_name
    text = (f"✅ স্বাগতম {first_name} 🎖️\n\n"
            "নীচের (ইনকাম শুরু করুন) বাটন থেকে Web Mini App খুলুন এবং আয় শুরু করুন।\n"
            "👉 ইনকাম শুরু করুন বাটনে চাপুন।\n\n"
            "বোঝার সুবিধার জন্য 🎬 টিউটোরিয়াল ভিডিও দেখে নিন।\n\n"
            "🎁 আপনি পেয়েছেন 50 পয়েন্ট বোনাস!")
    
    await update.message.reply_text(text, reply_markup=start_buttons())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = 7482645491 # আপনার আইডি
    
    if update.effective_user.id != ADMIN_ID:
        return

    # চেক করা হচ্ছে কোনো মেসেজকে রিপ্লাই দেওয়া হয়েছে কি না
    if update.message.reply_to_message:
        target_msg = update.message.reply_to_message
        users = get_all_users()
        
        # কমান্ড থেকে বাটন এবং লিঙ্ক আলাদা করা (যেমন: /broadcast নাম | লিঙ্ক)
        cmd_text = update.message.text.replace('/broadcast', '').strip()
        
        custom_markup = None
        if "|" in cmd_text:
            try:
                btn_name, btn_url = cmd_text.split("|")
                keyboard = [[InlineKeyboardButton(btn_name.strip(), url=btn_url.strip())]]
                custom_markup = InlineKeyboardMarkup(keyboard)
            except Exception:
                await update.message.reply_text("❌ ফরম্যাট ভুল! সঠিক নিয়ম: /broadcast বাটন নাম | লিঙ্ক")
                return

        success = 0
        for user_id in users:
            try:
                await context.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=update.effective_chat.id,
                    message_id=target_msg.message_id,
                    reply_markup=custom_markup # বাটন থাকলে যাবে, না থাকলে যাবে না
                )
                success += 1
            except Exception:
                continue
        
        await update.message.reply_text(f"✅ {success} জন ইউজারকে ব্রডকাস্ট পাঠানো হয়েছে।")
    else:
        await update.message.reply_text("⚠️ নিয়ম: যে মেসেজটি পাঠাতে চান সেটিকে Reply দিয়ে কমান্ড লিখুন।")

# ৪. মেইন বট রানার
if __name__ == '__main__':
    init_db()
    # আপনার বট টোকেনটি নিচে বসান
    TOKEN = "8584041971:AAGo2IcR2rE7mVWFUIXEh8F10Ld0jSMok-I" 
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    print("বটটি সফলভাবে চালু হয়েছে...")
    app.run_polling()
    import os
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello(): return "Bot is running!"
if __name__ == "__main__":
    # আপনার বটের মেইন রানার এখানে থাকবে
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

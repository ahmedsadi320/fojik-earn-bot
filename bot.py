import sqlite3
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- Flask keep-alive ----------
server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def add_user(user_id: int):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [u[0] for u in c.fetchall()]
    conn.close()
    return users

# ---------- START (REFERRAL FIXED) ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "User"

    # রেফারাল আইডি চেক করা
    ref_id = None
    if context.args and len(context.args) > 0:
        ref_id = context.args[0]

    # মিনি অ্যাপের লিঙ্ক তৈরি (startapp প্যারামিটার সহ)
    base_url = "https://mini-app2-pi.vercel.app/"
    
    # ইউজার যদি রেফারেল লিঙ্কে আসে, তবে startapp আইডি যোগ হবে
    if ref_id and str(ref_id) != str(user_id):
        app_url = f"{base_url}?startapp={ref_id}"
    else:
        app_url = base_url

    text = (
        f"𝐇𝐞𝐥𝐥𝐨 ❝{first_name}❞\n\n"
        "প্রিয় বন্ধু....🥰\n"
        "আমাদের ❝𝐅𝐨𝐣𝐢𝐤 𝐄𝐚𝐫𝐧❞ প্লাটফর্ম'টিতে যুক্ত হওয়ার জন্য আপনাকে ধন্যবাদ!🥰\n\n"
        "💸এখানে আপনি প্রতিদিন বিজ্ঞাপন(Ads) দেখে আয় করতে পারবেন।এবং আপনার বন্ধুকে আমন্ত্রণ জানিয়ে আয় করতে পারবেন।✅\n\n"
        "✉️যেকোনো প্রয়োজনে 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐓𝐞𝐚𝐦 এর সাথে যোগাযোগ করুন।\n"
        "🎬কিভাবে আয় করবেন 𝗧𝘂𝘁𝗼𝗿𝗶𝗮𝗹 ভিডিও দেখে শিখে নিতে পারেন।\n\n"
        "♻️নিচের 𝗢𝗽𝗲𝗻 𝗡𝗼𝘄 এ ক্লিক করে,সহজেই আয় করা শুরু করুন!\n"
        "❝ধন্যবাদ❞🥰"
    )

    keyboard = [
        [InlineKeyboardButton("✅𝗢𝗽𝗲𝗻 𝗡𝗼𝘄✅", web_app=WebAppInfo(url=app_url))],
        [InlineKeyboardButton("✅𝗢𝗽𝗲𝗻 𝗧𝘂𝘁𝗼𝗿𝗶𝗮𝗹✅", url="https://t.me/fojik_earn/17")]
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    

# ---------- BROADCAST ----------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_ID = 7482645491
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ নিয়ম: মেসেজটি Reply দিয়ে /broadcast লিখুন")
        return

    target_msg = update.message.reply_to_message
    users = get_all_users()

    cmd_text = update.message.text.replace("/broadcast", "").strip()
    custom_markup = None

    if "|" in cmd_text:
        try:
            btn_name, btn_url = cmd_text.split("|")
            keyboard = [[InlineKeyboardButton(btn_name.strip(), url=btn_url.strip())]]
            custom_markup = InlineKeyboardMarkup(keyboard)
        except:
            await update.message.reply_text("❌ ফরম্যাট: /broadcast বাটন | লিংক")
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
        except:
            continue

    await update.message.reply_text(f"✅ {success} জন ইউজারকে ব্রডকাস্ট পাঠানো হয়েছে")

# ---------- MAIN ----------
if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_flask).start()

    TOKEN = "8584041971:AAGo2IcR2rE7mVWFUIXEh8F10Ld0jSMok-I"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("Bot started...")
    app.run_polling()

import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- RENDER PORT FIX (FAKE SERVER) START ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running 24/7")

def run_fake_server():
    # Render hamesha PORT environment variable bhejta hai
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Fake server started on port {port}")
    server.serve_forever()

# Background thread mein server chalao taki bot block na ho
threading.Thread(target=run_fake_server, daemon=True).start()
# --- RENDER PORT FIX END ---

# 🔑 TOKEN: Render ke Environment Variables se uthayega
TOKEN = os.getenv('TOKEN', '8778371629:AAGjlowv2RNdipnw44REAndkGCEEGFaHrro')

# States
NAME, SCORE, SCHOOL, DISTRICT = range(4)

# Database (Note: Render restart hone par ye khali ho jayega)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏆 *𝐑𝐀𝐍𝐊𝐄𝐑 𝐏𝐑𝐎: 𝐂𝐋𝐀𝐒𝐒 𝟏𝟎 (𝟐𝟎𝟐𝟔)* 🏆\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ *Apna Rank check karne ke liye details bharein:* \n"
        "👤 Sabse pehle apna *Full Name* likhein:",
        parse_mode='Markdown'
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📊 Ab apna *Percentage (%)* bhejo (e.g. 96.5):", parse_mode='Markdown')
    return SCORE

async def get_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        score = float(update.message.text)
        if 0 <= score <= 100:
            context.user_data['score'] = score
            await update.message.reply_text("🏫 Apne *School ka Naam* likho:", parse_mode='Markdown')
            return SCHOOL
        else:
            await update.message.reply_text("❌ Percentage 0-100 ke beech likho!")
            return SCORE
    except:
        await update.message.reply_text("❌ Sirf number likho!")
        return SCORE

async def get_school(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['school'] = update.message.text
    await update.message.reply_text("📍 Apne *District* ka naam likho (e.g. Kushinagar):", parse_mode='Markdown')
    return DISTRICT

async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dist = update.message.text.strip().capitalize()
    data = {
        'name': context.user_data['name'],
        'score': context.user_data['score'],
        'school': context.user_data['school'],
        'district': dist
    }
    user_data[update.effective_user.id] = data
    await update.message.reply_text(
        f"✅ *𝐃𝐀𝐓𝐀 𝐒𝐀𝐕𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘!*\n\n"
        f"🏆 Rank dekhne ke liye `/rank` likho.\n"
        f"📍 Area wise dekhne ke liye `/district [Name]` likho.",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_data:
        await update.message.reply_text("📭 List abhi khali hai! Pehle `/start` karke detail dalo.")
        return

    sorted_list = sorted(user_data.values(), key=lambda x: x['score'], reverse=True)
    
    msg = "👑 *--- 𝐓𝐇𝐄 𝐄𝐋𝐈𝐓𝐄 𝐓𝐎𝐏𝐏𝐄𝐑𝐒 ---* 👑\n\n"
    for i, s in enumerate(sorted_list[:3]):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        msg += f"{medal} *𝐑𝐀𝐍𝐊 {i+1} - VIP STATUS*\n"
        msg += f"⭐ *Name:* {s['name']}\n"
        msg += f"🔥 *Score:* `{s['score']}%` | 📍 {s['district']}\n"
        msg += f"🏫 *School:* {s['school']}\n"
        msg += "--------------------------------\n"

    if len(sorted_list) > 3:
        msg += "\n📊 *--- 𝐆𝐄𝐍𝐄𝐑𝐀𝐋 𝐑𝐀𝐍𝐊𝐈𝐍𝐆𝐒 ---* 📊\n"
        for i, s in enumerate(sorted_list[3:15]):
            msg += f"🔹 *{i+4}.* {s['name']} — `{s['score']}%` ({s['district']})\n"

    msg += "\n━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🎁 *CHANNEL SPECIAL:* Rank 1 ko milega **Cash Prize!** 💰"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def district_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ *Usage:* `/district Kushinagar` likh kar bhejein.", parse_mode='Markdown')
        return

    target_dist = " ".join(context.args).capitalize()
    dist_list = [s for s in user_data.values() if s['district'] == target_dist]
    dist_list.sort(key=lambda x: x['score'], reverse=True)

    if not dist_list:
        await update.message.reply_text(f"❌ *{target_dist}* ka koi data nahi mila!")
        return

    msg = f"📍 *𝐓𝐎𝐏𝐏𝐄𝐑𝐒 𝐈𝐍 {target_dist.upper()}* 📍\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, s in enumerate(dist_list[:10]):
        rank_icon = "🏆" if i == 0 else "🔹"
        msg += f"{rank_icon} *Rank {i+1}:* {s['name']} — `{s['score']}%` \n"
        msg += f"🏫 {s['school']}\n\n"

    await update.message.reply_text(msg, parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_score)],
            SCHOOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_school)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
        },
        fallbacks=[],
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("rank", leaderboard))
    app.add_handler(CommandHandler("district", district_rank))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

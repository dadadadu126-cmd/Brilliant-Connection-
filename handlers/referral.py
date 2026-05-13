from telegram import Update
from telegram.ext import ContextTypes
from handlers.database import get_user, get_referral_count
from handlers.utils import format_balance
from config import REFERRAL_COMMISSION_PERCENT, EARNING_PER_AD


async def referral_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        user = query.from_user
        send = query.message.reply_text
    else:
        user = update.effective_user
        send = update.message.reply_text

    db_user = get_user(user.id)
    if not db_user:
        await send("❌ আগে /start দিন।")
        return

    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user.id}"
    ref_count = get_referral_count(user.id)
    commission_per_task = EARNING_PER_AD * (REFERRAL_COMMISSION_PERCENT / 100)

    msg = (
        f"🔗 *আপনার Referral লিংক*\n\n"
        f"`{ref_link}`\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"👥 মোট রেফার: *{ref_count} জন*\n\n"
        f"💰 প্রতি Task-এ কমিশন: *{format_balance(commission_per_task)}*\n\n"
        f"📢 পরিবার ও বন্ধুদের লিংক পাঠান!\n"
        f"যত বেশি রেফার = তত বেশি আয়! 🎯"
    )

    await send(msg, parse_mode="Markdown")

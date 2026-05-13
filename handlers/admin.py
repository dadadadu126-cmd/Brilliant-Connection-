from telegram import Update
from telegram.ext import ContextTypes
from handlers.database import get_pending_withdrawals, get_all_users
from handlers.utils import format_balance
from config import ADMIN_IDS


def is_admin(user_id):
    return user_id in ADMIN_IDS


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ আপনার অনুমতি নেই।")
        return

    pending = get_pending_withdrawals()
    total_users = len(get_all_users())

    msg = (
        f"🛠 *Admin Panel*\n\n"
        f"👥 মোট ইউজার: {total_users}\n"
        f"⏳ Pending Withdrawals: {len(pending)}\n\n"
    )

    if pending:
        msg += "📋 *Pending Requests:*\n"
        for row in pending[:10]:
            msg += (
                f"\n🔸 ID:{row['id']} | User:{row['user_id']}\n"
                f"   💰 {format_balance(row['amount'])} → {row['method']} {row['account_no']}\n"
                f"   📅 {row['request_date']}\n"
            )
    else:
        msg += "✅ কোনো pending request নেই।"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        return

    if not context.args:
        await update.message.reply_text("📢 ব্যবহার:\n/broadcast আপনার বার্তা")
        return

    message_text = " ".join(context.args)
    all_users = get_all_users()
    success = 0

    for uid in all_users:
        try:
            await context.bot.send_message(uid, f"📢 *বিজ্ঞপ্তি*\n\n{message_text}", parse_mode="Markdown")
            success += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ {success} জনকে পাঠানো হয়েছে!")

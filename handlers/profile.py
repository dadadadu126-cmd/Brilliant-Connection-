from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.database import get_user, get_today_task, get_referral_count, create_today_task
from handlers.utils import get_rank, get_next_rank, get_daily_task_limit, progress_bar, format_balance


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    rank = get_rank(db_user["total_tasks"])
    next_rank = get_next_rank(db_user["total_tasks"])
    ref_count = get_referral_count(user.id)
    task_limit = get_daily_task_limit(db_user["week_streak"])

    create_today_task(user.id, task_limit)
    today_task = get_today_task(user.id)
    today_done = today_task["tasks_done"] if today_task else 0

    if next_rank:
        current_min = rank["min_tasks"]
        tasks_in_rank = db_user["total_tasks"] - current_min
        tasks_needed = next_rank["min_tasks"] - current_min
        bar = progress_bar(tasks_in_rank, tasks_needed)
        rank_progress = (
            f"\n📈 *পরবর্তী Rank: {next_rank['name']}*\n"
            f"{bar}\n"
            f"আর {next_rank['min_tasks'] - db_user['total_tasks']} টি Task দরকার"
        )
    else:
        rank_progress = "\n👑 আপনি সর্বোচ্চ Rank-এ আছেন!"

    msg = (
        f"👤 *আপনার প্রোফাইল*\n"
        f"━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{user.id}`\n"
        f"📛 নাম: {db_user['full_name']}\n"
        f"📅 যোগ দিয়েছেন: {db_user['joined_date']}\n\n"
        f"🏅 *Rank: {rank['name']}*\n"
        f"📋 মোট Task: {db_user['total_tasks']}\n"
        f"📆 আজকের Task: {today_done}/{task_limit}\n"
        f"🔥 Streak: {db_user['week_streak']} সপ্তাহ\n\n"
        f"💰 ব্যালেন্স: *{format_balance(db_user['balance'])}*\n"
        f"📈 মোট আয়: {format_balance(db_user['total_earned'])}\n"
        f"🏧 উত্তোলন: {format_balance(db_user['total_withdrawn'])}\n\n"
        f"👥 রেফার: {ref_count} জন\n"
        f"{rank_progress}"
    )

    keyboard = [[
        InlineKeyboardButton("📋 Tasks", callback_data="view_tasks"),
        InlineKeyboardButton("🔗 Referral", callback_data="view_referral"),
        InlineKeyboardButton("💸 Withdraw", callback_data="view_withdraw"),
    ]]

    await send(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

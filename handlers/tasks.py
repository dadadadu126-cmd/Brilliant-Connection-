import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.database import (
    get_user, get_today_task, create_today_task,
    increment_task_done, update_balance, add_referral_earning
)
from handlers.utils import get_daily_task_limit, progress_bar, format_balance
from config import SAMPLE_ADS, EARNING_PER_AD, REFERRAL_COMMISSION_PERCENT


async def tasks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    task_limit = get_daily_task_limit(db_user["week_streak"])
    create_today_task(user.id, task_limit)
    today_task = get_today_task(user.id)

    done = today_task["tasks_done"]
    total = today_task["tasks_total"]

    if done >= total:
        msg = (
            f"🎉 *আজকের সব Task শেষ!*\n\n"
            f"✅ সম্পন্ন: {done}/{total} টি\n"
            f"💰 আজ আয়: {format_balance(done * EARNING_PER_AD)}\n\n"
            f"🕐 কাল আবার নতুন Tasks আসবে!"
        )
        await send(msg, parse_mode="Markdown")
        return

    ad = random.choice(SAMPLE_ADS)
    bar = progress_bar(done, total)

    msg = (
        f"📋 *আজকের Task ({done + 1}/{total})*\n\n"
        f"📢 *{ad['title']}*\n"
        f"{ad['description']}\n\n"
        f"🔗 [এখানে ক্লিক করে Ad দেখুন]({ad['url']})\n\n"
        f"⏱ কমপক্ষে {ad['watch_seconds']} সেকেন্ড দেখুন\n\n"
        f"📊 আজকের অগ্রগতি: {bar}\n"
        f"💵 এই task-এ আয়: {format_balance(EARNING_PER_AD)}"
    )

    keyboard = [[
        InlineKeyboardButton(
            "✅ Ad দেখলাম, পরের Task",
            callback_data=f"task_done_{ad['id']}"
        )
    ]]

    if query:
        await query.message.reply_text(msg, parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await send(msg, parse_mode="Markdown",
                   reply_markup=InlineKeyboardMarkup(keyboard))


async def task_done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Task সম্পন্ন!")

    user = query.from_user
    db_user = get_user(user.id)
    if not db_user:
        return

    today_task = get_today_task(user.id)
    if not today_task:
        return

    done = today_task["tasks_done"]
    total = today_task["tasks_total"]

    if done >= total:
        await query.message.reply_text("🎉 আজকের সব Task ইতিমধ্যে শেষ করেছেন!")
        return

    increment_task_done(user.id)
    update_balance(user.id, EARNING_PER_AD)

    if db_user["referred_by"]:
        commission = EARNING_PER_AD * (REFERRAL_COMMISSION_PERCENT / 100)
        update_balance(db_user["referred_by"], commission)
        add_referral_earning(db_user["referred_by"], user.id, commission)

    new_done = done + 1
    bar = progress_bar(new_done, total)

    if new_done >= total:
        msg = (
            f"🎉 *আজকের সব Task শেষ!*\n\n"
            f"✅ সম্পন্ন: {new_done}/{total}\n"
            f"💰 আজ মোট আয়: {format_balance(new_done * EARNING_PER_AD)}\n\n"
            f"📊 {bar}\n\n"
            f"🕐 কাল আবার নতুন Tasks!"
        )
        await query.message.reply_text(msg, parse_mode="Markdown")
    else:
        msg = (
            f"✅ *Task সম্পন্ন! +{format_balance(EARNING_PER_AD)} আয়!*\n\n"
            f"📊 {bar}\n\n"
            f"➡️ পরের Task দেখতে নিচের বাটন চাপুন।"
        )
        keyboard = [[InlineKeyboardButton("▶️ পরের Task", callback_data="view_tasks")]]
        await query.message.reply_text(
            msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
  )

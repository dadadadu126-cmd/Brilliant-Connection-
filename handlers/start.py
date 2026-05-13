from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.database import get_user, create_user, init_db
from handlers.utils import get_rank


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_db()
    user = update.effective_user
    args = context.args

    referred_by = None
    if args and args[0].startswith("ref_"):
        try:
            referred_by = int(args[0].replace("ref_", ""))
            if referred_by == user.id:
                referred_by = None
        except ValueError:
            referred_by = None

    existing = get_user(user.id)
    is_new = existing is None

    create_user(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        referred_by=referred_by if is_new else None
    )

    db_user = get_user(user.id)
    rank = get_rank(db_user["total_tasks"])

    welcome_msg = (
        f"🎉 *স্বাগতম, {user.first_name}!*\n\n"
        if is_new else
        f"👋 *আবার স্বাগতম, {user.first_name}!*\n\n"
    )

    if is_new and referred_by:
        welcome_msg += f"✅ আপনি একটি রেফারেল লিংকের মাধ্যমে যোগ দিয়েছেন!\n\n"

    welcome_msg += (
        f"🏅 আপনার Rank: *{rank['name']}*\n"
        f"💰 ব্যালেন্স: *৳{db_user['balance']:.2f}*\n\n"
        f"📢 প্রতিদিন Ads দেখুন এবং আয় করুন!\n"
        f"👨‍👩‍👧 পরিবারকে রেফার করুন, বেশি আয় করুন!\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("📋 আজকের Tasks", callback_data="view_tasks"),
            InlineKeyboardButton("👤 প্রোফাইল", callback_data="view_profile"),
        ],
        [
            InlineKeyboardButton("🔗 Referral লিংক", callback_data="view_referral"),
            InlineKeyboardButton("💸 Withdraw", callback_data="view_withdraw"),
        ],
    ]

    await update.message.reply_text(
        welcome_msg,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *কমান্ড লিস্ট*\n\n"
        "/start — বট শুরু করুন\n"
        "/tasks — আজকের Ads/Tasks দেখুন\n"
        "/profile — আপনার প্রোফাইল দেখুন\n"
        "/referral — রেফারেল লিংক পান\n"
        "/withdraw — টাকা তুলুন\n"
        "/help — সাহায্য\n\n"
        "💳 *৳400+ হলে বিকাশ/নগদে তুলুন!*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

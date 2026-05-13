from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.database import get_user, create_withdrawal
from handlers.utils import format_balance
from config import MIN_WITHDRAW, ADMIN_IDS

_withdraw_state = {}


async def withdraw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    balance = db_user["balance"]

    if balance < MIN_WITHDRAW:
        msg = (
            f"💰 *ন্যূনতম {format_balance(MIN_WITHDRAW)} দরকার*\n\n"
            f"আপনার ব্যালেন্স: *{format_balance(balance)}*\n"
            f"আরো দরকার: *{format_balance(MIN_WITHDRAW - balance)}*\n\n"
            f"📋 /tasks করুন এবং প্রতিদিন Ad দেখুন!"
        )
        await send(msg, parse_mode="Markdown")
        return

    _withdraw_state[user.id] = {"step": "choose_method", "balance": balance}

    keyboard = [[
        InlineKeyboardButton("📱 বিকাশ", callback_data="withdraw_bkash"),
        InlineKeyboardButton("💚 নগদ", callback_data="withdraw_nagad"),
    ]]
    await send(
        f"💸 *Withdraw Request*\n\n💰 ব্যালেন্স: *{format_balance(balance)}*\n\nকোন মাধ্যমে নিতে চান?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def withdraw_submit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    state = _withdraw_state.get(user.id)
    if not state:
        return

    step = state.get("step")

    if step == "enter_account":
        account_no = update.message.text.strip()
        if len(account_no) != 11 or not account_no.isdigit():
            await update.message.reply_text("❌ সঠিক ১১ ডিজিটের নম্বর দিন।")
            return
        state["account_no"] = account_no
        state["step"] = "enter_amount"
        _withdraw_state[user.id] = state
        await update.message.reply_text(
            f"💵 কত টাকা তুলতে চান?\n_(সর্বোচ্চ {format_balance(state['balance'])})_",
            parse_mode="Markdown"
        )

    elif step == "enter_amount":
        try:
            amount = float(update.message.text.strip())
        except ValueError:
            await update.message.reply_text("❌ সঠিক পরিমাণ লিখুন (যেমন: 400)")
            return

        db_user = get_user(user.id)
        if amount < MIN_WITHDRAW:
            await update.message.reply_text(f"❌ ন্যূনতম {format_balance(MIN_WITHDRAW)} তুলতে হবে।")
            return
        if amount > db_user["balance"]:
            await update.message.reply_text(f"❌ ব্যালেন্স কম। বর্তমান: {format_balance(db_user['balance'])}")
            return

        method = state["method"]
        account_no = state["account_no"]
        create_withdrawal(user.id, amount, method, account_no)
        del _withdraw_state[user.id]

        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🔔 *নতুন Withdraw!*\n👤 {db_user['full_name']} (ID: {user.id})\n"
                    f"💰 {format_balance(amount)}\n📱 {method}: {account_no}",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

        await update.message.reply_text(
            f"✅ *Request সফল!*\n💰 {format_balance(amount)}\n📱 {method}: {account_no}\n\n⏳ ২৪-৪৮ ঘণ্টার মধ্যে পাঠানো হবে।",
            parse_mode="Markdown"
        )

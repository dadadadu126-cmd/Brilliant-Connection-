import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bot.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY,
            username        TEXT,
            full_name       TEXT,
            referred_by     INTEGER DEFAULT NULL,
            joined_date     TEXT,
            total_tasks     INTEGER DEFAULT 0,
            balance         REAL    DEFAULT 0.0,
            total_earned    REAL    DEFAULT 0.0,
            total_withdrawn REAL    DEFAULT 0.0,
            week_streak     INTEGER DEFAULT 0,
            last_week_tasks INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            task_date   TEXT,
            tasks_done  INTEGER DEFAULT 0,
            tasks_total INTEGER DEFAULT 5
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            amount      REAL,
            method      TEXT,
            account_no  TEXT,
            status      TEXT DEFAULT 'pending',
            request_date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS referral_earnings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referee_id  INTEGER,
            amount      REAL,
            earn_date   TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return user


def create_user(user_id, username, full_name, referred_by=None):
    conn = get_conn()
    conn.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, full_name, referred_by, joined_date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, full_name, referred_by, str(date.today())))
    conn.commit()
    conn.close()


def update_balance(user_id, amount):
    conn = get_conn()
    conn.execute("""
        UPDATE users SET balance = balance + ?, total_earned = total_earned + ?
        WHERE user_id = ?
    """, (amount, amount, user_id))
    conn.commit()
    conn.close()


def get_referral_count(user_id):
    conn = get_conn()
    count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE referred_by=?", (user_id,)
    ).fetchone()[0]
    conn.close()
    return count


def get_all_users():
    conn = get_conn()
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [u["user_id"] for u in users]


def get_today_task(user_id):
    today = str(date.today())
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM daily_tasks WHERE user_id=? AND task_date=?",
        (user_id, today)
    ).fetchone()
    conn.close()
    return row


def create_today_task(user_id, tasks_total):
    today = str(date.today())
    conn = get_conn()
    conn.execute("""
        INSERT OR IGNORE INTO daily_tasks (user_id, task_date, tasks_total)
        VALUES (?, ?, ?)
    """, (user_id, today, tasks_total))
    conn.commit()
    conn.close()


def increment_task_done(user_id):
    today = str(date.today())
    conn = get_conn()
    conn.execute("""
        UPDATE daily_tasks SET tasks_done = tasks_done + 1
        WHERE user_id=? AND task_date=?
    """, (user_id, today))
    conn.execute("""
        UPDATE users SET total_tasks = total_tasks + 1 WHERE user_id=?
    """, (user_id,))
    conn.commit()
    conn.close()


def create_withdrawal(user_id, amount, method, account_no):
    conn = get_conn()
    conn.execute("""
        INSERT INTO withdrawals (user_id, amount, method, account_no, request_date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, method, account_no, str(date.today())))
    conn.execute("""
        UPDATE users SET balance = balance - ?, total_withdrawn = total_withdrawn + ?
        WHERE user_id = ?
    """, (amount, amount, user_id))
    conn.commit()
    conn.close()


def get_pending_withdrawals():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM withdrawals WHERE status='pending' ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


def approve_withdrawal(wid):
    conn = get_conn()
    conn.execute("UPDATE withdrawals SET status='approved' WHERE id=?", (wid,))
    conn.commit()
    conn.close()


def add_referral_earning(referrer_id, referee_id, amount):
    conn = get_conn()
    conn.execute("""
        INSERT INTO referral_earnings (referrer_id, referee_id, amount, earn_date)
        VALUES (?, ?, ?, ?)
    """, (referrer_id, referee_id, amount, str(date.today())))
    conn.commit()
    conn.close()

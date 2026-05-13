from config import RANKS, BASE_DAILY_TASKS, TASKS_INCREMENT_PER_WEEK


def get_rank(total_tasks):
    current = RANKS[0]
    for rank in RANKS:
        if total_tasks >= rank["min_tasks"]:
            current = rank
    return current


def get_next_rank(total_tasks):
    for rank in RANKS:
        if total_tasks < rank["min_tasks"]:
            return rank
    return None


def get_daily_task_limit(week_streak):
    return BASE_DAILY_TASKS + (week_streak * TASKS_INCREMENT_PER_WEEK)


def format_balance(amount):
    return f"৳{amount:.2f}"


def progress_bar(done, total, length=10):
    filled = int((done / total) * length) if total > 0 else 0
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {done}/{total}"

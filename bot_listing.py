from telegram.ext import Updater, MessageHandler, Filters
import os
import csv
import json
import signal
import traceback
from datetime import datetime

# ====== CONFIG ======
BOT_TOKEN = "bot_token_here"  # <-- put your token here
CSV_FILE = "group_info.csv"        # clean structured data (Timestamp, Group Name, Chat ID)
LOG_FILE = "group_raw_log.txt"     # raw log with full update JSON envelope

# ANSI colors
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


# ====== CSV (group list) ======
def init_csv():
    """Create CSV with header if missing."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Group Name", "Chat ID"])  # header


def is_chat_logged(chat_id: str) -> bool:
    """Return True if chat_id already exists in CSV."""
    if not os.path.exists(CSV_FILE):
        return False
    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row.get("Chat ID", "")).strip() == str(chat_id):
                    return True
    except Exception as e:
        # Do not spam console with data; keep it quiet
        _log_error_to_file("csv_read_error", str(e))
    return False


def append_group_to_csv(timestamp: str, group_name: str, chat_id: str):
    """Append a new group row to CSV."""
    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, group_name, chat_id])
    except Exception as e:
        _log_error_to_file("csv_write_error", str(e))


# ====== RAW LOG (TXT) ======
def log_action(action: str, results: dict = None):
    """
    Write one line: [timestamp] - action - <minified JSON or nothing>
    For updates, results will be: {"ok":true,"result":[<full update dict>]}
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if results is None:
        line = f"[{ts}] - {action}"
    else:
        # Minified JSON, keep unicode characters
        payload = json.dumps(results, ensure_ascii=False, separators=(",", ":"))
        line = f"[{ts}] - {action} - {payload}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        # As a last resort, print a simple error (no user data)
        print(f"Raw log write error: {e}")


def _log_error_to_file(action: str, err_text: str):
    """Internal helper to log non-sensitive errors into the raw log."""
    log_action(action, {"error": err_text})


# ====== HANDLERS ======
def handle_update(update, context):
    """
    - Append group (once) to CSV
    - Raw log txt: full Telegram update envelope (ok/result)
    - Console: ONLY "Already logged: ..." in yellow (for existing groups)
    """
    try:
        chat = update.effective_chat
        if chat and chat.type in ["group", "supergroup"]:
            group_name = chat.title
            chat_id = chat.id
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # CSV: keep one row per group
            if not is_chat_logged(chat_id):
                append_group_to_csv(ts, group_name, str(chat_id))
                # Per your request: do NOT print anything for new groups
            else:
                # Console (Yellow): Already logged
                print(f"{YELLOW}[{ts}] - Already logged: {group_name} | {chat_id}{RESET}")

        # Raw log: full update object wrapped like a getUpdates response
        full_update = update.to_dict()
        envelope = {"ok": True, "result": [full_update]}
        log_action("update_received", envelope)

    except Exception as e:
        _log_error_to_file("handle_update_error", f"{type(e).__name__}: {e}")
        traceback.print_exc()


def heartbeat(context):
    """Console-only heartbeat (Magenta) to avoid blank window."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{MAGENTA}[{ts}] - Polling at: {ts}{RESET}")


# ====== SHUTDOWN ======
def signal_handler(sig, frame):
    # Keep shutdown message minimal; you didn't restrict this
    print("Bot shutting down gracefully.")
    raise SystemExit(0)


# ====== MAIN ======
def main():
    signal.signal(signal.SIGINT, signal_handler)

    init_csv()

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handle all updates/messages
    dp.add_handler(MessageHandler(Filters.all, handle_update))

    # Polling heartbeat every 10s (console only)
    updater.job_queue.run_repeating(heartbeat, interval=10, first=0)

    # Start polling (Updater handles Telegram getUpdates internally)
    updater.start_polling(poll_interval=1.0)
    # You didn't forbid startup line; keeping it so you know it launched
    print("Bot started. Press Ctrl+C to stop.")
    updater.idle()


if __name__ == "__main__":
    main()

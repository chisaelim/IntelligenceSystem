"""Send a test message (and a photo) through TelegramNotifier, the class the camera will use.

    python -m tools.notify_test --dry-run                   print what would be sent
    python -m tools.notify_test                             really send (needs .env)
    python -m tools.notify_test --photo output/day07_overlay.jpg
"""
import argparse

from intelligence import PROJECT_ROOT
from intelligence.config import load_env
from intelligence.telegram_bot import TelegramNotifier


def main():
    ap = argparse.ArgumentParser(description="Send a test alert through TelegramNotifier")
    ap.add_argument("--dry-run", action="store_true", help="print the alert instead of sending it")
    ap.add_argument("--photo", help="a picture to send with a caption")
    args = ap.parse_args()

    env = load_env(PROJECT_ROOT / ".env")
    token, chat_id = env.get("TELEGRAM_BOT_TOKEN", ""), env.get("TELEGRAM_CHAT_ID", "")
    if not args.dry_run and (not token or not chat_id):
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the .env file (or use --dry-run).")

    notifier = TelegramNotifier(token, chat_id, dry_run=args.dry_run)
    print("Queueing the messages...")
    notifier.send_text("Test message from the notifier")
    if args.photo:
        notifier.send_photo(args.photo, "Test alert: person, at night\n2026-01-01 12:00:00  (person #1)")

    notifier.flush()  # wait until everything has really gone out
    print("Done.")


if __name__ == "__main__":
    main()

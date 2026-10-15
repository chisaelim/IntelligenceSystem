"""Check your Telegram settings (token and chat id in .env).

    python -m tools.telegram_check                      who is my bot?
    python -m tools.telegram_check --send               also send a test message
    python -m tools.telegram_check --photo some.jpg     also send a picture
"""
import argparse

import requests

from intelligence import PROJECT_ROOT
from intelligence.config import load_env


def call(token, method, data=None, files=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        return requests.post(url, data=data, files=files, timeout=20)
    except requests.RequestException as error:
        # Print only the type: the message would contain the URL, and the URL contains the token.
        raise SystemExit(f"Could not reach Telegram: {type(error).__name__}")


def report(what, reply):
    try:
        data = reply.json()
    except ValueError:
        data = {}
    if data.get("ok"):
        print(f"{what}: sent")
    else:
        raise SystemExit(f"{what} failed: {data.get('description')} (status {reply.status_code})")


def main():
    ap = argparse.ArgumentParser(description="Check the Telegram settings in .env")
    ap.add_argument("--send", action="store_true", help="send a test message")
    ap.add_argument("--photo", help="send this picture too")
    args = ap.parse_args()

    env = load_env(PROJECT_ROOT / ".env")
    token, chat_id = env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("Put TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the .env file first.")

    reply = call(token, "getMe")
    info = reply.json()
    if not info.get("ok"):
        raise SystemExit(f"Telegram refused the token: {info.get('description')} (status {reply.status_code})")
    print("Bot found: @" + info["result"]["username"])

    if args.send:
        report("message", call(token, "sendMessage", data={"chat_id": chat_id, "text": "Hello from my Intelligence System!"}))
    if args.photo:
        with open(args.photo, "rb") as f:
            report("photo", call(token, "sendPhoto", data={"chat_id": chat_id, "caption": "Test photo"}, files={"photo": f}))


if __name__ == "__main__":
    main()

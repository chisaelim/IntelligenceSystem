"""Find your Telegram chat id. First send any message to your bot in Telegram, then run:

    python -m tools.telegram_chat_id
"""
import requests

from intelligence import PROJECT_ROOT
from intelligence.config import load_env


def main():
    token = load_env(PROJECT_ROOT / ".env").get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Put TELEGRAM_BOT_TOKEN in the .env file first.")

    try:
        reply = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
    except requests.RequestException as error:
        # Print only the type: the message would contain the URL, and the URL contains the token.
        raise SystemExit(f"Could not reach Telegram: {type(error).__name__}")

    data = reply.json()
    if not data.get("ok"):
        raise SystemExit(f"Telegram refused the token: {data.get('description')} (status {reply.status_code})")

    chats = {}
    for update in data["result"]:
        message = update.get("message") or update.get("channel_post") or {}
        chat = message.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("first_name") or chat.get("title") or chat.get("username") or "?"

    if not chats:
        raise SystemExit("No messages found. Open your bot in Telegram, press Start, send 'hello', and run this again.")
    for chat_id, name in chats.items():
        print(f"chat id {chat_id}  ({name})")
    print("Copy the number into TELEGRAM_CHAT_ID in your .env file.")


if __name__ == "__main__":
    main()

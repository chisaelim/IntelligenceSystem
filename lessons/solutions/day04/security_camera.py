from intelligence import PROJECT_ROOT
from intelligence.config import load_config, load_env, project_path


def main():
    cfg = load_config()
    env = load_env(PROJECT_ROOT / ".env")

    print("Watching:", ", ".join(cfg["watch_classes"]))
    print("Database file:", project_path(cfg["paths"]["database"]))
    print("Telegram token set:", bool(env.get("TELEGRAM_BOT_TOKEN")))
    print("Telegram chat id set:", bool(env.get("TELEGRAM_CHAT_ID")))


if __name__ == "__main__":
    main()

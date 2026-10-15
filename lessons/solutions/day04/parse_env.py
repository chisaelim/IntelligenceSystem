from pathlib import Path


def load_env(path):
    """Read KEY=VALUE lines from a .env file into a dict."""
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = load_env(Path(".env"))
print("keys found:", sorted(env))
print("token length:", len(env.get("TELEGRAM_BOT_TOKEN", "")))

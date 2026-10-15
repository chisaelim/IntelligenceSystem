import json
import sys


def load_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"Config file not found: {path}")
    except json.JSONDecodeError as error:
        raise SystemExit(f"{path} is not valid JSON (line {error.lineno}, column {error.colno}): {error.msg}")


path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
cfg = load_config(path)
print("loaded", len(cfg), "settings from", path)

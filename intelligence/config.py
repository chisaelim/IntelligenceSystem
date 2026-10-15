import json
from pathlib import Path

from . import PROJECT_ROOT


def load_env(path):
    """Read KEY=VALUE lines from a .env file into a plain dict (nothing is exported)."""
    values = {}
    if not path.is_file():
        return values
    # utf-8-sig: Windows Notepad may save a BOM that would otherwise glue itself to the first key.
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(path=None):
    path = Path(path) if path else PROJECT_ROOT / "config.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def project_path(relative):
    """Resolve a config path against the project folder (absolute paths pass through)."""
    p = Path(relative)
    return p if p.is_absolute() else PROJECT_ROOT / p

import tempfile
from pathlib import Path

from intelligence import PROJECT_ROOT
from intelligence.config import load_config, load_env, project_path

# load_env: comments and blank lines are skipped, quotes are removed, only the first "=" splits
with tempfile.TemporaryDirectory() as folder:
    env_file = Path(folder) / ".env"
    env_file.write_text('# comment\n\nTOKEN="abc=123"\nCHAT_ID = 42\nbroken line\n', encoding="utf-8")
    assert load_env(env_file) == {"TOKEN": "abc=123", "CHAT_ID": "42"}
assert load_env(Path("does-not-exist.env")) == {}

# project_path: relative paths start at the project folder, absolute paths are left alone
assert project_path("data/events.db") == PROJECT_ROOT / "data" / "events.db"
assert project_path(PROJECT_ROOT) == PROJECT_ROOT

# load_config: the real config.json has the settings we need
cfg = load_config()
for key in ("watch_classes", "label_severity", "night_hours", "alert", "paths"):
    assert key in cfg, f"config.json is missing {key!r}"

print("config OK")

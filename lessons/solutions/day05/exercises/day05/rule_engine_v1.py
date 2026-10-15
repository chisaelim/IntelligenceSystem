import json


class RuleEngine:
    """Decides how much a sighting matters. For now it only knows the settings."""

    def __init__(self, cfg, store=None):
        self.cfg = cfg
        self.store = store
        self.zones = [z for z in cfg["zones"] if z.get("enabled", True)]

    def describe(self):
        return f"RuleEngine with {len(self.zones)} active zone(s)"


with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

engine = RuleEngine(cfg)
print(engine.describe())

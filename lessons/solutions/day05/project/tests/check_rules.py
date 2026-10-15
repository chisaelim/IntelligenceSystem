from datetime import datetime

from intelligence.config import load_config
from intelligence.rules import RuleEngine

engine = RuleEngine(load_config())  # night_hours = 22:00 -> 06:00

assert engine.is_night(datetime(2026, 1, 1, 23, 30))  # late evening
assert engine.is_night(datetime(2026, 1, 2, 0, 0))  # midnight
assert engine.is_night(datetime(2026, 1, 2, 5, 59))  # just before morning
assert not engine.is_night(datetime(2026, 1, 2, 6, 0))  # morning starts at 06:00 exactly
assert not engine.is_night(datetime(2026, 1, 2, 12, 0))  # noon
assert not engine.is_night(datetime(2026, 1, 2, 21, 59))  # just before night
assert engine.is_night(datetime(2026, 1, 2, 22, 0))  # night starts at 22:00 exactly

# A "night" that does not cross midnight (01:00 -> 05:00)
cfg = load_config()
cfg["night_hours"] = ["01:00", "05:00"]
short_night = RuleEngine(cfg)
assert short_night.is_night(datetime(2026, 1, 2, 3, 0))
assert not short_night.is_night(datetime(2026, 1, 2, 23, 0))

print("rules OK")

from datetime import datetime

from intelligence.config import load_config
from intelligence.rules import RuleEngine

cfg = load_config()
cfg["zones"][0]["enabled"] = True  # front_door: x from 0.15 to 0.85, y from 0.25 to 0.95 of the picture
cfg["anomaly"]["enabled"] = False  # the history rule has its own test (check_history.py)
engine = RuleEngine(cfg)

NOON = datetime(2026, 3, 11, 12, 0)
NIGHT = datetime(2026, 3, 11, 23, 30)

# The night rule from Day 5, including the border cases
assert engine.is_night(NIGHT)
assert engine.is_night(datetime(2026, 1, 2, 5, 59))
assert not engine.is_night(datetime(2026, 1, 2, 6, 0))
assert not engine.is_night(NOON)
assert engine.is_night(datetime(2026, 1, 2, 22, 0))

# A "night" that does not cross midnight (01:00 -> 05:00)
short_cfg = load_config()
short_cfg["night_hours"] = ["01:00", "05:00"]
short_night = RuleEngine(short_cfg)
assert short_night.is_night(datetime(2026, 1, 2, 3, 0))
assert not short_night.is_night(datetime(2026, 1, 2, 23, 0))

# assess: base severity, +1 at night, +1 in a zone, never more than 3
assert engine.assess("person", set(), NOON).severity == 2
assert engine.assess("person", set(), NIGHT).severity == 3
assert engine.assess("car", set(), NOON).severity == 1
assert engine.assess("car", set(), NIGHT).severity == 2
assert engine.assess("car", {"front_door"}, NIGHT).severity == 3
assert engine.assess("person", {"front_door"}, NIGHT).severity == 3  # 2 + 1 + 1 = 4, capped at 3
assert engine.assess("dog", {"front_door"}, NIGHT).severity == 0  # base 0 means: never an alert
assert engine.assess("suitcase", set(), NOON).severity == 1  # a label without a rule counts as 1
assert engine.assess("person", {"front_door"}, NIGHT).describe() == "person, at night, in front_door"

# zones_for: the FEET (bottom centre of the box) decide, and the zone must watch that label
frame_shape = (1000, 1000, 3)  # a picture 1000 pixels high and wide
inside = (400, 300, 600, 900)  # feet at (500, 900): inside the zone
outside = (400, 300, 600, 980)  # feet at (500, 980): 98% down, below the zone (which ends at 95%)
assert engine.zones_for("person", inside, frame_shape) == ["front_door"]
assert engine.zones_for("person", outside, frame_shape) == []
assert engine.zones_for("car", inside, frame_shape) == []  # this zone only watches persons

# zone_polygons: only enabled zones are returned
cfg["zones"][0]["enabled"] = False
assert RuleEngine(cfg).zone_polygons(frame_shape) == []

print("rules OK")

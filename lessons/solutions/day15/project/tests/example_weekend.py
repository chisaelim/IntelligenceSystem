"""An example test for an OWN rule: "a sighting at the weekend is more serious".

Add the rule to RuleEngine.assess first (see the lesson), then save this file as
tests/check_weekend.py and run:   python -m tests.check_weekend
"""
from datetime import datetime

from intelligence.config import load_config
from intelligence.rules import RuleEngine

cfg = load_config()
cfg["anomaly"]["enabled"] = False  # keep the history rule out of this test
engine = RuleEngine(cfg)

WEDNESDAY_NOON = datetime(2026, 3, 11, 12, 0)
SATURDAY_NOON = datetime(2026, 3, 14, 12, 0)
assert WEDNESDAY_NOON.weekday() == 2 and SATURDAY_NOON.weekday() == 5  # Monday is 0, Sunday is 6

assert engine.assess("car", set(), WEDNESDAY_NOON).severity == 1  # an ordinary weekday: unchanged
assert engine.assess("car", set(), SATURDAY_NOON).severity == 2  # the weekend: one point more
assert engine.assess("person", set(), SATURDAY_NOON).describe() == "person, at the weekend"
assert engine.assess("dog", set(), SATURDAY_NOON).severity == 0  # a dog is still never an alert

print("weekend rule OK")

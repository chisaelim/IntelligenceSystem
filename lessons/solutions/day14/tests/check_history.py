import random
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from intelligence.config import load_config
from intelligence.events import EventStore
from intelligence.rules import RuleEngine


def add_history(store, count):
    """Pretend sightings of a person between 08:00 and 17:59 on past days."""
    random.seed(1)
    for number in range(count):
        when = (datetime.now() - timedelta(days=1 + number % 20)).replace(
            hour=random.randint(8, 17), minute=random.randint(0, 59), second=0, microsecond=0)
        store.add("appeared", track_id=number, label="person", severity=2, ts=when)


THREE_AM = datetime(2026, 3, 11, 3, 0)
NOON = datetime(2026, 3, 11, 12, 0)
EVENING = datetime(2026, 3, 11, 23, 0)

with tempfile.TemporaryDirectory() as folder:
    store = EventStore(Path(folder) / "events.db")
    cfg = load_config()

    # 1. Too little history (10 sightings, but min_history is 30): the rule says nothing
    add_history(store, 10)
    assert not RuleEngine(cfg, store).is_unusual("person", THREE_AM)

    # 2. Enough history (100 sightings): 03:00 and 23:00 never happened, noon is normal.
    #    (A new RuleEngine, because each engine remembers its answers for ten minutes.)
    store.db.execute("DELETE FROM events")
    add_history(store, 100)
    engine = RuleEngine(cfg, store)
    assert engine.is_unusual("person", THREE_AM)
    assert engine.is_unusual("person", EVENING)
    assert not engine.is_unusual("person", NOON)

    # 3. It changes the severity and explains itself
    night = engine.assess("person", set(), THREE_AM)
    assert night.severity == 3
    assert night.describe() == "person, at night, unusual for this hour"
    day = engine.assess("person", set(), NOON)
    assert day.severity == 2 and day.describe() == "person"

    # 4. A label with no history of its own is never unusual (a car at noon is still just a car)
    assert not engine.is_unusual("car", THREE_AM)

    # 5. The rule can be switched off in config.json
    cfg["anomaly"]["enabled"] = False
    assert not RuleEngine(cfg, store).is_unusual("person", THREE_AM)

    store.close()

print("history OK")

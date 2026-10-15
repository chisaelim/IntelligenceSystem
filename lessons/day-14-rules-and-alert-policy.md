# Day 14: Making it intelligent

**Hours 40-42 of 45** · **Milestone 8:** `intelligence/rules.py` complete (severity, zones, "unusual for this hour") plus the alert policy · **Checkpoint 3** (threads, YOLO, tracking, rules)

## What you can do at the end of today

- Write the rule engine that gives every sighting a severity from 0 to 3 **and the reasons**.
- Decide which zone a person is in from the position of their feet.
- Teach the system what is **normal** from its own history, and make it notice what is not.
- Write the alert policy: when to send, when to wait, when to send again.
- See your camera program print `appeared (HIGH: person, at night, in front_door)` and `ALERT` lines.

## Where today fits in the project

You have a camera that sees and follows people. It does not yet know what **matters**. A cat at noon: ignore. A person at the front door at 3 a.m.: wake me up. Today you write that judgement. This is the "intelligence" of the Intelligence System, in the old sense of the word: **perceive** (YOLO), **remember** (the database), **reason** (the rules), and, tomorrow, **act** (the Telegram alert).

```text
label ─┐
zones ─┤                                        ┌─► severity 0-3
time  ─┼─► RuleEngine.assess() ─► Assessment ───┤
history┘   (base + night + zone + unusual)      └─► reasons: "person, at night, in front_door"
                                                          │
                                  should_alert(severity, ...)  ──► send an alert, or stay quiet
```

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 40 | 5 | Warm-up: what is `lost_seconds` for? |
| | 15 | Talk: the severity score, zones and feet |
| | 40 | **Lab 14.1** `Assessment`, `zones_for`, `assess` |
| 41 | 15 | Talk: learning what is normal from history |
| | 45 | **Lab 14.2** `hour_histogram`, `is_unusual`, try it with the demo history |
| 42 | 15 | Talk: the alert policy |
| | 20 | **Lab 14.3 (Milestone 8)** `should_alert` and the camera loop |
| | 20 | **Checkpoint 3** (quiz) |
| | 5 | Wrap-up |

---

# Hour 40: Severity, zones and reasons

## Learn

The `RuleEngine` answers one question: **how much does this sighting matter?** The answer is an `Assessment`: a severity number and the list of reasons. You built the idea on Days 2 and 3. Today it becomes a class with all the ingredients:

| Ingredient | Points | Comes from |
|---|---|---|
| Base severity of the label | 0 to 3 (0 = "log it, never alert") | `label_severity` in `config.json`; a label with no rule counts as 1 |
| It is night | +1 | `night_hours` (Day 5) |
| It is inside a zone | +1 | `zones` in `config.json` |
| It is unusual for this hour | +1 | the history (hour 41) |
| **Maximum** | **3** | |

| Severity | Name | What it means in practice |
|---|---|---|
| 0 | ignored | logged only, never an alert (a dog, a cat) |
| 1 | low | a car, a bicycle... worth a line in the log |
| 2 | medium | a person: an alert is sent (the default `min_severity` is 2) |
| 3 | HIGH | a person at night, or in a zone, or at an unusual hour |

The **reasons** matter. A phone message `HIGH: person, at night, in front_door` is far more useful than `severity 3`.

### Which zone is a person in?

On Day 7 you learned that a zone is a polygon and that we test the **feet** (bottom centre of the box) against it with `cv2.pointPolygonTest`. Each zone in `config.json` also has a `watch` list: the labels it applies to (`["person"]`). A car driving through the "front door" zone is not interesting. So `zones_for(label, box, frame_shape)` returns the names of the zones where this label's feet are inside.

## Lab 14.1: `Assessment`, `zones_for` and `assess`

You will make `intelligence/rules.py` complete. Today's first half:

**Step 1.** Add the imports, the constants and the `Assessment` dataclass at the top of the file (the history constants are used in the next hour):

**`intelligence/rules.py`** top of the file

```python
import time as time_module
from dataclasses import dataclass, field
from datetime import time

import cv2
import numpy as np

SEVERITY_NAMES = {0: "ignored", 1: "low", 2: "medium", 3: "HIGH"}
HISTORY_DAYS = 30
HISTORY_CACHE_SECONDS = 600


@dataclass
class Assessment:
    severity: int
    reasons: list = field(default_factory=list)

    def describe(self):
        return ", ".join(self.reasons)
```

- `SEVERITY_NAMES` turns `0..3` into words (a dictionary, Day 3).
- `Assessment` is a dataclass (Day 5) with a `severity` and a list of `reasons`. Its method `describe()` joins the reasons with commas: `"person, at night, in front_door"`.

**Step 2.** Add `zones_for` and a first, empty version of `is_unusual` to the class `RuleEngine`. The real `is_unusual` is the next hour's work. For now it answers "no, nothing is unusual", so you can test the rest:

```python
    def is_unusual(self, label, now):
        """True if this label is rare at this hour compared with its own history."""
        return False  # we write the real version in hour 41
```

**`intelligence/rules.py`** add inside class RuleEngine

```python
    def zones_for(self, label, box, frame_shape):
        """Names of zones containing the bottom-centre of the box (where the object touches the ground)."""
        x1, y1, x2, y2 = box
        foot = ((x1 + x2) / 2, y2)
        names = []
        for zone, (name, polygon) in zip(self.zones, self.zone_polygons(frame_shape)):
            if label in zone.get("watch", [label]) and cv2.pointPolygonTest(polygon, foot, False) >= 0:
                names.append(name)
        return names
```

How it works: `zip(self.zones, self.zone_polygons(frame_shape))` walks through two lists in parallel: the zone settings and the polygons in pixels (from Day 7). `foot` is the bottom centre of the box. A zone counts when it watches this label **and** `cv2.pointPolygonTest(...) >= 0` (inside, or exactly on the edge).

**Step 3.** Add `assess`:

**`intelligence/rules.py`** add inside class RuleEngine

```python
    def assess(self, label, zones, now):
        base = self.cfg["label_severity"].get(label, 1)
        if base == 0:
            return Assessment(0, [label])  # labels set to 0 are logged but never escalate

        score, reasons = base, [label]
        if self.is_night(now):
            score += 1
            reasons.append("at night")
        if zones:
            score += 1
            reasons.append("in " + ", ".join(sorted(zones)))
        if self.is_unusual(label, now):
            score += 1
            reasons.append("unusual for this hour")
        return Assessment(min(score, 3), reasons)
```

Read it as a recipe:

1. `base` is the label's number from the config (`1` if the label is not listed).
2. A base of `0` returns at once: the **guard clause** from Day 2.
3. Start from `base`, add a reason for each modifier. (`", ".join(sorted(zones))` turns `{"front_door", "driveway"}` into `"driveway, front_door"`.)
4. `min(score, 3)` keeps the severity at most 3.

## Test it

Create `tests/check_rules.py`. It is the Day 5 night test, extended with every rule of `assess` and `zones_for`. The inputs are chosen so you can calculate the answer by hand:

**`tests/check_rules.py`**

```python
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
```

```text
$ python -m tests.check_rules
rules OK
```

Read the test as a specification. For example: a person at night in a zone is `2 + 1 + 1 = 4`, but the severity is **3** (the cap). A dog is **0**, whatever else is true. And the `outside` box has its feet at 98% of the height, just below the zone, so it is *not* in the zone even though most of the person is inside it.

## Check yourself

1. What is the severity of a car, at night, in a zone? Show the sum.
2. Why does the zone test use the bottom of the box and not the centre?
3. Why do we write reasons and not only a number?

<details><summary>Answers</summary>

1. `1 + 1 + 1 = 3` (the car's base is 1; but only if the zone's `watch` list includes `car`. With the default zone, which watches only persons, the car gets `1 + 1 = 2`).
2. The feet show where the person stands on the ground. The centre of the box can look inside the zone when the person stands behind it.
3. So the message tells the human why it matters, and so you can debug the rules: "why was this HIGH?"

</details>

---

# Hour 41: Learning what is normal

## Learn

Some things are not suspicious because of **what** they are, but because of **when** they happen. A person at 12:00 is normal in a shop. The same person at 03:00 is not. The system does not need to be told your opening hours: it can **learn** them from its own memory.

The idea (from Day 9):

> For this label, look at the last 30 days. Count how many sightings happened **in this hour of the day**. If that is a tiny share of all sightings, this hour is **unusual**.

```text
share  =  sightings in this hour  /  all sightings of this label
unusual if   total ≥ min_history (30)   and   share < rare_share (0.02 = 2%)
```

Two safety rules are built into the definition:

- `min_history`: with fewer than 30 sightings the system says **nothing**. A few sightings are not a pattern, and on its first day every hour would be "unusual".
- The comparison is **per label**: the history of persons does not say anything about cars.

This is a very simple kind of machine learning: the system learns a pattern (a **histogram** of hours) from data. No neural network is needed.

### The histogram query

First we need to count sightings per hour. In `events.py` add `timedelta` to the import and the method `hour_histogram`:

**`intelligence/events.py`** the import at the top of the file

```python
from datetime import datetime, timedelta
```

**`intelligence/events.py`** add inside class EventStore

```python
    def hour_histogram(self, label, days):
        """How often `label` appeared in each hour of the day over the last `days` days."""
        since = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
        rows = self.db.execute(
            "SELECT CAST(strftime('%H', ts) AS INTEGER), COUNT(*) FROM events "
            "WHERE kind = 'appeared' AND label = ? AND ts >= ? GROUP BY 1",
            (label, since),
        ).fetchall()
        return dict(rows)
```

It is the SQL of Day 9 with two changes. It has `?` placeholders for the label and for the earliest date (`now - timedelta(days=30)`, as ISO text), and it counts only `appeared` events. It returns a dictionary such as `{8: 12, 9: 15, 10: 11}`: hour number to count. (`dict(rows)` turns a list of pairs into a dictionary.)

Update the test `tests/check_events.py` so that it covers it. The new part builds events with chosen times and checks that only the right label, the right kind of event, and the last 30 days are counted:

**`tests/check_events.py`**

```python
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from intelligence.events import EventStore

with tempfile.TemporaryDirectory() as folder:
    store = EventStore(Path(folder) / "sub" / "events.db")  # also creates the folder "sub"

    store.add("appeared", track_id=1, label="person", severity=2, detail="person")
    store.add("zone_enter", track_id=1, label="person", zone="front_door", severity=3)
    store.add("alert", track_id=1, label="person", severity=3, alerted=True, snapshot="a.jpg")
    store.add("appeared", track_id=2, label="car", severity=1)
    store.add("left", track_id=1, label="person", severity=3, detail="seen 12s")

    rows = store.recent(3)
    assert len(rows) == 3
    assert rows[0][1] == "left"  # newest first
    assert rows[0][7] == "seen 12s"

    summary = store.today_summary()
    assert ("person", 1, 1) in summary  # 1 appeared, 1 alert
    assert ("car", 1, 0) in summary

    # An event from yesterday is not in today's summary
    store.add("appeared", track_id=3, label="dog", severity=0, ts=datetime.now() - timedelta(days=1))
    assert not any(label == "dog" for label, _, _ in store.today_summary())


    # hour_histogram: how often did this label appear in each hour of the day (last N days)?
    history = EventStore(Path(folder) / "history.db")
    base = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=2)
    for hour in (8, 8, 9, 14):
        history.add("appeared", label="person", ts=base.replace(hour=hour))
    history.add("appeared", label="car", ts=base.replace(hour=8))  # another label: not counted
    history.add("left", label="person", ts=base.replace(hour=8))  # another kind of event: not counted
    history.add("appeared", label="person", ts=base.replace(hour=20) - timedelta(days=60))  # too old
    assert history.hour_histogram("person", 30) == {8: 2, 9: 1, 14: 1}
    history.close()

    store.close()

print("events OK")
```

```text
$ python -m tests.check_events
events OK
```

### `is_unusual`

First give the engine a place to keep the answers it has worked out (the cache is explained below). Add **one line at the end of `__init__`**:

**`intelligence/rules.py`** the whole __init__, with the new last line

```python
    def __init__(self, cfg, store=None):
        self.cfg = cfg
        self.store = store
        self.zones = [z for z in cfg["zones"] if z.get("enabled", True)]
        self.night_start = _parse_hm(cfg["night_hours"][0])
        self.night_end = _parse_hm(cfg["night_hours"][1])
        self._unusual_cache = {}  # (label, hour) -> (expires_at, is_unusual)
```

Then replace the stub in `rules.py` with the real method:

**`intelligence/rules.py`** replace the empty is_unusual

```python
    def is_unusual(self, label, now):
        """True if this label is rare at this hour compared with its own history."""
        anomaly = self.cfg["anomaly"]
        if not anomaly["enabled"] or self.store is None:  # no history to compare with
            return False
        key = (label, now.hour)
        cached = self._unusual_cache.get(key)
        if cached and cached[0] > time_module.monotonic():
            return cached[1]

        histogram = self.store.hour_histogram(label, HISTORY_DAYS)
        total = sum(histogram.values())
        unusual = total >= anomaly["min_history"] and histogram.get(now.hour, 0) / total < anomaly["rare_share"]
        self._unusual_cache[key] = (time_module.monotonic() + HISTORY_CACHE_SECONDS, unusual)
        return unusual
```

Read it:

1. `anomaly["enabled"]` lets you switch the rule off in `config.json`. And if there is no history database (`self.store is None`, as in your earlier tests) it also says "no".
2. **The cache.** `assess` runs for every tracked object on every frame, about 30 times per second. Asking the database every time would be wasteful, and the answer almost never changes. So the answer is remembered for `HISTORY_CACHE_SECONDS` (10 minutes), per `(label, hour)`. `time_module.monotonic()` is the stopwatch from Day 5. We import the module as `time_module` because the file already has `from datetime import time` (a different thing with the same name!).
3. `histogram.get(now.hour, 0) / total` is the share of this hour. If this hour is not in the dictionary, it is 0.
4. The result is `total >= min_history and share < rare_share`.

Finally, make sure `assess` uses it, with the three lines you already wrote:

```python
        if self.is_unusual(label, now):
            score += 1
            reasons.append("unusual for this hour")
```

## Test it with a pretend history

`tests/check_history.py` builds temporary histories and checks five situations: too little history (10 sightings: nothing is unusual), enough history (100 sightings: 03:00 and 23:00 are unusual, noon is not), that it changes the severity and explains itself, that a label with no history of its own is never unusual, and that the rule can be switched off:

**`tests/check_history.py`**

```python
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
```

```text
$ python -m tests.check_history
history OK
```

Note the comment in step 2: each `RuleEngine` keeps its own cache for ten minutes, so the test creates a **new** engine after changing the history.

## Ask the engine questions

To explore the rules without waiting for night, use a small tool. It asks the engine about a pretend sighting at any hour, comparing with the demo history you made on Day 9 (`data/demo_events.db`, 100 persons between 08:00 and 17:59). If you do not have it, create it with `python -m tools.seed_history`.

**`tools/explain_rules.py`**

```python
"""Ask the rule engine how serious a pretend sighting would be, without waiting for the right time of day.

    python -m tools.explain_rules --label person --hour 3
    python -m tools.explain_rules --label person --hour 23 --zone front_door
    python -m tools.explain_rules --label car --hour 12 --db data/events.db
"""
import argparse
from datetime import datetime

from intelligence.config import load_config, project_path
from intelligence.events import EventStore
from intelligence.rules import SEVERITY_NAMES, RuleEngine


def main():
    ap = argparse.ArgumentParser(description="Explain the severity of a pretend sighting")
    ap.add_argument("--label", default="person")
    ap.add_argument("--hour", type=int, default=12, help="hour of the day, 0 to 23")
    ap.add_argument("--zone", action="append", default=[], help="a zone the object is in (can be repeated)")
    ap.add_argument("--db", default="data/demo_events.db", help="the history to compare with")
    args = ap.parse_args()

    path = project_path(args.db)
    if not path.is_file():
        raise SystemExit(f"History file not found: {path}. Create one with: python -m tools.seed_history")

    engine = RuleEngine(load_config(), EventStore(path))
    when = datetime.now().replace(hour=args.hour, minute=0, second=0, microsecond=0)
    assessment = engine.assess(args.label, set(args.zone), when)
    print(f"{args.label} at {args.hour:02d}:00 -> {SEVERITY_NAMES[assessment.severity]} "
          f"({assessment.severity}): {assessment.describe()}")


if __name__ == "__main__":
    main()
```


Try some hours:

```text
$ python -m tools.explain_rules --label person --hour 12
person at 12:00 -> medium (2): person
```

```text
$ python -m tools.explain_rules --label person --hour 3
person at 03:00 -> HIGH (3): person, at night, unusual for this hour
```

```text
$ python -m tools.explain_rules --label person --hour 23 --zone front_door
person at 23:00 -> HIGH (3): person, at night, in front_door, unusual for this hour
```

```text
$ python -m tools.explain_rules --label car --hour 3
car at 03:00 -> medium (2): car, at night
```

```text
$ python -m tools.explain_rules --label dog --hour 3
dog at 03:00 -> ignored (0): dog
```

Read each answer and explain it with the rules:

- A person at **noon**: base 2, nothing else. Medium.
- A person at **03:00**: base 2, +1 night, +1 unusual (no sighting in the history was at 03:00). HIGH.
- A person at **23:00 in the front door zone**: 2 + 1 + 1 + 1 = 5, capped at 3. HIGH, with all four reasons.
- A **car at 03:00**: base 1, +1 night. There is no history of cars, so nothing is unusual: medium.
- A **dog**: ignored, always.

## Check yourself

1. Why does `is_unusual` need `min_history`?
2. What is the share of 03:00 in the demo history? Is a person at 03:00 unusual?
3. Why is the answer cached?
4. What happens to a person at 12:00 if your history contains only sightings at night?

<details><summary>Answers</summary>

1. With only a few sightings there is no pattern. On the first day every hour would look "unusual" and every alert would be HIGH.
2. 0%, because no sighting happened at 03:00. It is below 2%, and there are 100 sightings (more than 30), so yes, it is unusual.
3. `assess` runs on every frame for every object. The answer changes very slowly, so asking the database 30 times per second would waste time for no benefit.
4. Noon would be unusual. The system learns whatever "normal" is from the data. If the data is wrong, its judgement is wrong. This is an important lesson about all machine learning.

</details>

---

# Hour 42: The alert policy (Milestone 8)

## Learn

A severity is not yet a decision. If the program sent a message for **every frame** in which a person is medium or HIGH, your phone would explode (30 messages a second!). We need rules about **when to speak**:

1. **Severe enough.** Only when `severity >= min_severity` (2 by default). Low sightings are logged, not sent.
2. **Once per object.** A person standing at the door is one alert, not a hundred. Each track remembers the highest severity it has already been alerted about (`alerted_severity`).
3. **Escalation.** But if the same person becomes **more serious** (a medium person walks into the zone and becomes HIGH), it is news: alert again.
4. **Cooldown.** Even for different objects, do not send more than one alert per `cooldown_seconds` (30), or ten people walking in together would send ten messages.
5. **HIGH never waits.** A severity 3 ignores the cooldown. If it is serious, you want to know now.

Written as a table:

| Severity | Already alerted at | Seconds since last alert | Alert? | Why |
|---|---|---|---|---|
| 1 | 0 | any | no | below `min_severity` |
| 2 | 0 | 10 000 | **yes** | first alert for this object |
| 2 | 2 | 10 000 | no | already told you (once per object) |
| 3 | 2 | 10 000 | **yes** | it became more serious |
| 2 | 0 | 5 | no | cooldown, 5 of 30 seconds passed |
| 3 | 0 | 5 | **yes** | HIGH ignores the cooldown |

This is a **pure function**: it only looks at its inputs and answers yes or no. It does not use a clock, print or send anything. That makes it very easy to test.

## Lab 14.3 (Milestone 8): `should_alert`

Add this function at the end of `intelligence/rules.py` (outside the class):

**`intelligence/rules.py`** add at the end of rules.py

```python
def should_alert(severity, alerted_severity, seconds_since_last_alert, alert_cfg):
    """The alert policy.

    An object causes an alert when it is serious enough, only once, and again only if it becomes
    more serious. Alerts are also spaced out by a cooldown, but a HIGH alert never waits.
    """
    worth_alerting = severity >= alert_cfg["min_severity"] and severity > alerted_severity
    cooled_down = seconds_since_last_alert >= alert_cfg["cooldown_seconds"] or severity == 3
    return worth_alerting and cooled_down
```

Test it with the table above. `tests/check_policy.py` has one `assert` for each row:

**`tests/check_policy.py`**

```python
from intelligence.rules import should_alert

alert_cfg = {"min_severity": 2, "cooldown_seconds": 30}
LONG_AGO = 10_000  # seconds since the last alert

# Below the minimum severity: never an alert
assert not should_alert(1, 0, LONG_AGO, alert_cfg)
assert not should_alert(0, 0, LONG_AGO, alert_cfg)

# The first alert of a track
assert should_alert(2, 0, LONG_AGO, alert_cfg)

# The same track, same severity: only once
assert not should_alert(2, 2, LONG_AGO, alert_cfg)

# The track becomes more serious: alert again
assert should_alert(3, 2, LONG_AGO, alert_cfg)

# Cooldown: another alert 5 seconds after the last one is held back ...
assert not should_alert(2, 0, 5, alert_cfg)
# ... unless it is HIGH
assert should_alert(3, 0, 5, alert_cfg)

# Exactly at the end of the cooldown
assert should_alert(2, 0, 30, alert_cfg)
assert not should_alert(2, 0, 29.9, alert_cfg)

print("policy OK")
```

```text
$ python -m tests.check_policy
policy OK
```

### The camera loop with rules

Now use the rules in `intelligence/app.py`. The changes compared with Day 13:

1. Open the `EventStore` and give it to the `RuleEngine` (the history rule needs it). Close it in `finally`.
2. When a track is **confirmed**: find its zones, assess it, and print the severity and the reasons.
3. On every frame, for a confirmed track: report **new zones** (the set difference from Day 3: `set(zones_for(...)) - t.zones`), re-assess (the time or the zone may have changed), keep the severity in the track (the overlay uses it for the colour), and ask `should_alert`.
4. If it says yes, remember the time and the severity and print an `ALERT` line. We do **not** send anything yet: that is tomorrow.

Here is the complete file:

**`intelligence/app.py`**

```python
import argparse
import time
from dataclasses import dataclass, field
from datetime import datetime

import cv2

from .config import load_config, project_path
from .events import EventStore
from .rules import SEVERITY_NAMES, RuleEngine, should_alert

SEVERITY_COLORS = {0: (160, 160, 160), 1: (0, 200, 0), 2: (0, 165, 255), 3: (0, 0, 255)}  # BGR


@dataclass
class Track:
    track_id: int
    label: str
    first_seen: float
    last_seen: float
    box: tuple = (0, 0, 0, 0)
    frames: int = 0
    confirmed: bool = False
    zones: set = field(default_factory=set)
    severity: int = 0
    alerted_severity: int = 0


def parse_source(value):
    """A camera number ("0" or 0) becomes an int. Anything else is a video file name."""
    return int(value) if str(value).isdigit() else value


def draw_overlay(frame, tracks, rules, now):
    for name, polygon in rules.zone_polygons(frame.shape):
        pts = polygon.astype("int32")
        cv2.polylines(frame, [pts], True, (255, 200, 0), 1)
        cv2.putText(frame, name, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)

    for t in tracks:
        x1, y1, x2, y2 = (int(v) for v in t.box)
        color = SEVERITY_COLORS[t.severity] if t.confirmed else (120, 120, 120)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 if t.confirmed else 1)
        text = f"{t.label} #{t.track_id}"
        if t.zones:
            text += " [" + ",".join(sorted(t.zones)) + "]"
        cv2.putText(frame, text, (x1, max(y1 - 6, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    cv2.putText(frame, f"{now:%Y-%m-%d %H:%M:%S}", (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def main():
    ap = argparse.ArgumentParser(description="Webcam security camera")
    ap.add_argument("--source", help="camera index or video file (overrides config)")
    ap.add_argument("--no-window", action="store_true", help="run without the preview window")
    args = ap.parse_args()

    cfg = load_config()
    store = EventStore(project_path(cfg["paths"]["database"]))  # the rules read the history from it
    rules = RuleEngine(cfg, store)

    # Imported here so the program starts fast until it really needs the detector (loading PyTorch takes seconds).
    from .detector import Detector

    model_path = project_path(cfg["paths"]["models"]) / cfg["model"]
    model_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {model_path.name} ...")
    detector = Detector(model_path, cfg["watch_classes"], cfg["confidence"], cfg["image_size"], cfg["device"])

    source = parse_source(args.source if args.source is not None else cfg["source"])
    is_file = isinstance(source, str)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(
            f"Cannot open source {source!r}. For a camera on macOS, allow camera access for your "
            "terminal/VS Code in System Settings > Privacy & Security > Camera."
        )

    min_frames = cfg["min_track_frames"]
    lost_after = cfg["lost_seconds"]
    alert_cfg = cfg["alert"]
    tracks = {}  # track id -> Track
    last_alert = 0.0  # time.time() of the last alert

    def finish_track(t):
        if t.confirmed:
            print(f"[{datetime.now():%H:%M:%S}] {t.label} #{t.track_id} left after {t.last_seen - t.first_seen:.0f}s")

    print(f"Running on {detector.device}. Press q to quit.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                if is_file:
                    break
                print("Camera read failed, retrying...")
                time.sleep(0.5)
                continue

            now, clock = datetime.now(), time.monotonic()
            seen_ids = set()

            for det in detector.track(frame):
                seen_ids.add(det.track_id)
                t = tracks.get(det.track_id)
                if t is None:
                    t = tracks[det.track_id] = Track(det.track_id, det.label, clock, clock)
                t.last_seen, t.box, t.label = clock, det.box, det.label
                t.frames += 1

                if not t.confirmed and t.frames >= min_frames:
                    t.confirmed = True
                    t.zones.update(rules.zones_for(t.label, t.box, frame.shape))
                    a = rules.assess(t.label, t.zones, now)
                    print(f"[{now:%H:%M:%S}] {t.label} #{t.track_id} appeared ({SEVERITY_NAMES[a.severity]}: {a.describe()})")
                if not t.confirmed:
                    continue

                # Entering a zone is reported once per zone.
                for zone in set(rules.zones_for(t.label, t.box, frame.shape)) - t.zones:
                    t.zones.add(zone)
                    print(f"[{now:%H:%M:%S}] {t.label} #{t.track_id} entered {zone}")

                a = rules.assess(t.label, t.zones, now)
                t.severity = a.severity

                if should_alert(a.severity, t.alerted_severity, time.time() - last_alert, alert_cfg):
                    last_alert = time.time()
                    t.alerted_severity = a.severity
                    print(f"[{now:%H:%M:%S}] ALERT {SEVERITY_NAMES[a.severity]}: {a.describe()} "
                          f"({t.label} #{t.track_id})  [not sent yet]")

            lost = [tid for tid, t in tracks.items() if tid not in seen_ids and clock - t.last_seen > lost_after]
            for tid in lost:
                finish_track(tracks.pop(tid))

            if not args.no_window:
                draw_overlay(frame, [t for t in tracks.values() if t.track_id in seen_ids], rules, now)
                cv2.imshow("Security Camera", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        for t in tracks.values():
            finish_track(t)
        cap.release()
        cv2.destroyAllWindows()
        store.close()
```

Run it on your clip (with the default `config.json` the zone is switched off). The times and severities you see depend on the time of day: the rules use the real clock.

If you run it at night (22:00 to 05:59), every person gets `+1` and appears as HIGH. During the day they are medium.

## Try it with the zone switched on

Open `config.json` and set `"enabled": true` for the `front_door` zone. Run again. The sample clip, with the zone on, gives this (your clip and your time of day will give something different):

```text
[20:32:23] bus #1 appeared (low: bus)
[20:32:23] person #2 appeared (medium: person)
[20:32:23] ALERT medium: person (person #2)  [not sent yet]
[20:32:23] person #3 appeared (HIGH: person, in front_door)
[20:32:23] ALERT HIGH: person, in front_door (person #3)  [not sent yet]
[20:32:23] person #4 appeared (HIGH: person, in front_door)
[20:32:23] ALERT HIGH: person, in front_door (person #4)  [not sent yet]
[20:32:23] person #5 appeared (medium: person)
```

Read this like a detective:

- The **bus** is only `low`: no alert (below `min_severity`).
- **Person #2** is medium: **alert**, the first one.
- **Persons #3 and #4** have their feet inside the zone: HIGH, so they ignore the cooldown: **alerts** right away.
- **Person #5** is medium, but **no alert**: it is only a few moments after #2's alert, the 30-second cooldown is running, and medium must wait.

And one more experiment. Make a history that does **not** contain the hour you are working in, so that "unusual for this hour" appears. For example, if it is daytime now:

```bash
python -m tools.seed_history --first-hour 1 --last-hour 4 --replace
```

Point your config at it by copying `config.json` to `config.demo.json` and changing `"database"` under `"paths"` to `"data/demo_events.db"` (we do this properly tomorrow). The program will say `unusual for this hour` for persons. Tomorrow's `--config` option will let you run it with `python security_camera.py --config config.demo.json`.

## Tuning with recorded clips

You now have a lot of settings. The right way to choose them is to **test with recorded clips**, not to guess. For a clip with a person walking in and out, answer:

| Question | Setting to look at |
|---|---|
| Does it announce things that are not there? | raise `confidence` or `min_track_frames` |
| Does it miss you or announce late? | lower `confidence`; check light; check `image_size` |
| Does it say "left" too early or too late? | `lost_seconds` |
| Too many alerts for one visit? | raise `cooldown_seconds`; check that `alerted_severity` works |
| Too few alerts? | lower `min_severity` to 1 |

Change **one** setting at a time and run the same clip again.

## Checkpoint 3: threads, YOLO, tracking and rules (20 minutes)

Closed book, no running code. One point per question: 15 points.

1. What does "blocking" mean, and why must the camera loop not block while sending a Telegram message?
2. Why does `send_text` return immediately?
3. What does `flush()` do, and why is it called before the program ends?
4. What is a `--dry-run` for?
5. Name the three things in a detection.
6. What does the tracker add to detection?
7. What does `persist=True` do?
8. What is `result.boxes.id` when nothing is being tracked?
9. What happens when you raise the confidence threshold a lot?
10. Name the setting that says how many frames a track must be seen before it is announced.
11. Calculate the severity of a person, at night, inside a zone, at an unusual hour.
12. Calculate the severity of a car at night, outside every zone, at a normal hour.
13. A track has severity 2, was never alerted, and the last alert was 10 seconds ago (cooldown 30). Is there an alert? What if its severity is 3?
14. Which point of the box decides if someone is in a zone?
15. Why does the rule engine need `min_history`?

<details><summary>Answer key (instructor)</summary>

Computed by Python:

```pycon
>>> min(2 + 1 + 1 + 1, 3)
3
>>> min(1 + 1, 3)
2
```

The answers:

1. The program stops and waits for a slow operation, so it cannot read frames. The camera would be blind for seconds.
2. It only puts the message in a queue; a worker thread sends it.
3. It waits until the queue is empty. The worker is a daemon thread and would be stopped with the program, losing unsent messages.
4. To test without sending real messages: it prints what would be sent.
5. A box, a class (label) and a confidence.
6. A stable id per object over time (so we can count, time and alert once per object).
7. It keeps the tracker's memory between frames.
8. `None`.
9. You get fewer false alarms but you start to miss real objects.
10. `min_track_frames`.
11. 3 (`2 + 1 + 1 + 1 = 5`, capped at 3).
12. 2 (`1 + 1`).
13. No (medium, cooldown not over). Yes if it is 3 (HIGH ignores the cooldown).
14. The bottom centre (the feet).
15. With too little history there is no pattern, and everything would look unusual.

**Scoring:** 13-15 excellent, 10-12 good, 7-9 needs support before Day 15, below 7 meet the student today. Tomorrow assembles everything, so a student who does not understand the rules and the policy needs help now.

</details>

---

# Day 14 wrap-up

## Checklist

- [ ] `tests.check_rules`, `tests.check_history`, `tests.check_policy` and `tests.check_events` all pass.
- [ ] `python -m tools.explain_rules --hour 3` gives HIGH with the reason `unusual for this hour`.
- [ ] `python security_camera.py --source clip.mp4 --no-window` prints severities and `ALERT` lines.
- [ ] You can explain the five parts of the alert policy.
- [ ] You tuned one setting using your clip and explained the effect.
- [ ] You finished Checkpoint 3.
- [ ] You committed (`git commit -m "Day 14: rules, history and alert policy"`).

## Your project folder today

```text
my-intelligence-system/
├── intelligence/
│   ├── rules.py                <- complete: Assessment, zones_for, is_unusual, assess, should_alert
│   ├── events.py               <- hour_histogram added
│   ├── app.py                  <- rules and alert policy in the loop
│   └── ...
├── tools/
│   └── explain_rules.py        <- new
└── tests/
    ├── check_rules.py          <- extended
    ├── check_history.py        <- new
    ├── check_policy.py         <- new
    └── check_events.py         <- extended
```

Solutions are in [`solutions/day14/project/`](solutions/day14/project/).

## Instructor notes

- **This is the day where the project becomes "intelligent".** Spend time on the examples: let students predict the severity of each sighting before they run `explain_rules`. When a prediction is wrong, find out which rule they forgot.
- **Caches confuse students.** If someone changes the history and sees no effect, they are looking at a cached answer. The test shows the fix: a new `RuleEngine`.
- **Stub-first working** (writing `is_unusual` as `return False` first) is a good professional habit: make the whole thing work, then improve one part.
- **Show the lie in "learning".** Change the history to night-only and show that noon becomes unusual. Machine learning learns what the data says, good or bad. Ask: "who decides what is normal for a family's door camera?"
- **Privacy and bias:** a system that flags "unusual" people can be unfair. Mention that this one only looks at *when*, not at who.
- **Cooldown arguments:** students will want 0 (all alerts). Ask them to calculate: 30 frames per second, one person standing for a minute, no policy: how many messages?
- **If you are behind:** write `should_alert` together on the board (it is five lines), skip the "tuning" table, and keep the rules test. Day 15 needs `rules.py` complete and `app.py` with the loop.
- **Fast finishers:** add a new rule to `assess`, for example "+1 if the object is very large (close to the camera)" or "+1 when a person has been in view for more than 60 seconds", with a test for it.

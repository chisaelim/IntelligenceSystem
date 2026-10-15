# Day 5: Objects, time and git

**Hours 13-15 of 45** · **Milestone 2:** data classes (`Detection`, `Track`) and the night-time rule (`RuleEngine.is_night`) · **Checkpoint 1** (Python quiz)

## What you can do at the end of today

- Write a **class** with attributes and methods, and create objects from it.
- Use a **dataclass** to hold related data (a detection, a track) in a few lines.
- Work with dates and times: `datetime`, `time`, `timedelta`, and formatting.
- Write the rule "is it night?" so it also works when night crosses midnight.
- Save your work with **git** and keep secrets out of it.
- Show what you know in Checkpoint 1.

## Where today fits in the project

The project is made of **objects** that remember things and do things:

| Object | Remembers | Does | You build it on |
|---|---|---|---|
| `Detection` | one thing the detector found | (just holds data) | today |
| `Track` | one object followed over time | (just holds data) | today |
| `RuleEngine` | the settings | decides how serious a sighting is | today and Day 14 |
| `EventStore` | the database | saves and reads events | Day 9 |
| `TelegramNotifier` | token, chat id, a queue | sends alerts | Day 11 |
| `Detector` | the YOLO model | finds and tracks objects | Day 13 |

Today you write the first two kinds, and the first rule of the `RuleEngine`: **is it night?** You also start using git so that your work is saved and your secrets are safe.

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 13 | 5 | Warm-up: ask a student to explain `.get()` |
| | 20 | Talk: classes, objects, `self`, methods |
| | 10 | Live demo |
| | 25 | **Labs 5.1-5.2** A counter class, a `RuleEngine` skeleton |
| 14 | 15 | Talk: dataclasses, `datetime`, `time` |
| | 10 | Live demo |
| | 35 | **Labs 5.3-5.4 (Milestone 2)** `Detection`, `Track`, `is_night` |
| 15 | 15 | Talk and demo: git, `.gitignore`, secrets |
| | 10 | **Lab 5.5** First commit |
| | 20 | **Checkpoint 1** (quiz) |
| | 15 | Review the quiz answers |

---

# Hour 13: Classes and objects

## Learn

A **class** is a plan for making objects. An **object** bundles **data** (attributes) and **actions** (methods). You have used objects already: a string is an object and `.upper()` is its method.

```pycon
>>> class Camera:
...     def __init__(self, name, fps):
...         self.name = name
...         self.fps = fps
...         self.frames_read = 0
...     def read(self):
...         self.frames_read += 1
...     def describe(self):
...         return f"{self.name}: {self.frames_read} frames at {self.fps} fps"
...
>>> front = Camera("front door", 30)
>>> garage = Camera("garage", 15)
>>> front.read()
>>> front.read()
>>> front.describe()
'front door: 2 frames at 30 fps'
>>> garage.describe()
'garage: 0 frames at 15 fps'
>>> front.frames_read
2
```

(Normally you leave a blank line between methods. We left them out so the example can be typed into the console.)

Read the class:

- `class Camera:` starts the plan.
- `__init__` is the **constructor**. Python calls it when you write `Camera("front door", 30)`. Its job is to set the starting attributes.
- **`self`** is the object itself. Every method has `self` as its first parameter. `self.name = name` stores the value **in the object**, so `front` and `garage` each keep their own name and frame count.
- `read` and `describe` are **methods**: functions that belong to the object. You call them with a dot: `front.read()`.

**Why not just use functions and a dictionary?** A class keeps the data and the code that works on it in one place. You do not pass the same settings to ten functions. The `RuleEngine` stores the config once and then answers questions like "is it night?".

## Lab 5.1: A sighting counter

Turn the counting code from Day 3 into a class. Create `exercises/day05/counter.py`.

**`exercises/day05/counter.py`**

```python
class SightingCounter:
    """Counts how many times each label was seen."""

    def __init__(self):
        self.counts = {}

    def add(self, label):
        self.counts[label] = self.counts.get(label, 0) + 1

    def total(self):
        return sum(self.counts.values())

    def most_common(self):
        return max(self.counts, key=self.counts.get)


counter = SightingCounter()
for label in ["person", "car", "person", "person", "dog"]:
    counter.add(label)

print("total sightings:", counter.total())
print("most common:", counter.most_common())
print("counts:", counter.counts)
```

```text
$ python exercises/day05/counter.py
total sightings: 5
most common: person
counts: {'person': 3, 'car': 1, 'dog': 1}
```

**Try:** create two counters and add different labels to each. Do they interfere with each other? (No: each object has its own `counts`.)

## Lab 5.2: A `RuleEngine` skeleton

Start the class that will become the brain of the project. For now it only stores the settings and picks out the zones that are switched on. Create `exercises/day05/rule_engine_v1.py` (run it from the project folder, where `config.json` is).

**`exercises/day05/rule_engine_v1.py`**

```python
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
```

```text
$ python exercises/day05/rule_engine_v1.py
RuleEngine with 0 active zone(s)
```

The interesting line is `self.zones = [z for z in cfg["zones"] if z.get("enabled", True)]`. It is a list comprehension (Day 3) that keeps only the zones that are not disabled. `.get("enabled", True)` means: if a zone has no `enabled` setting, count it as enabled.

`store=None` is a **default value**. The engine will need the event database later (Day 9), but today it does not exist yet, so we make it optional.

**Try:** copy `config.json` to `config_test.json`, set `"enabled": true` for the zone, load that file instead, and see `1 active zone(s)`.

## Check yourself

1. What does `self` mean inside a method?
2. When is `__init__` called?
3. If you create `a = SightingCounter()` and `b = SightingCounter()` and call `a.add("car")`, what is `b.counts`?

<details><summary>Answers</summary>

1. The object the method was called on. `self.name` is "this object's name".
2. Automatically, once, when you create the object: `SightingCounter()`.
3. `{}` (empty). `a` and `b` are separate objects with separate dictionaries.

</details>

---

# Hour 14: Dataclasses, dates and the night rule (Milestone 2)

## Learn: dataclasses

Many classes only hold data and need a boring `__init__` that copies each argument into an attribute. A **dataclass** writes that for you. You list the fields with their types:

```pycon
>>> from dataclasses import dataclass, field
>>> @dataclass
... class Detection:
...     track_id: int
...     label: str
...     confidence: float
...     box: tuple
...
>>> d = Detection(1, "person", 0.91, (47, 400, 239, 904))
>>> d
Detection(track_id=1, label='person', confidence=0.91, box=(47, 400, 239, 904))
>>> d.label
'person'
>>> d.box[0]
47
>>> d == Detection(1, "person", 0.91, (47, 400, 239, 904))
True
```

You get `__init__`, a readable printout (`__repr__`) and `==` for free. Fields can have **default values**:

```pycon
>>> from dataclasses import dataclass
>>> @dataclass
... class Counter:
...     name: str
...     count: int = 0
...     confirmed: bool = False
...
>>> Counter("people")
Counter(name='people', count=0, confirmed=False)
>>> Counter("cars", 5)
Counter(name='cars', count=5, confirmed=False)
```

### The mutable default trap

A default value that is a list, set or dictionary would be **shared** by every object. Python refuses it:

```pycon
>>> from dataclasses import dataclass
>>> try:
...     @dataclass
...     class Bad:
...         zones: set = set()
... except ValueError as error:
...     print(error)
...
mutable default <class 'set'> for field zones is not allowed: use default_factory
```

The fix is `field(default_factory=set)`. It means "make a **new** empty set for each object":

```pycon
>>> from dataclasses import dataclass, field
>>> @dataclass
... class Track:
...     track_id: int
...     zones: set = field(default_factory=set)
...
>>> a = Track(1)
>>> b = Track(2)
>>> a.zones.add("front_door")
>>> a
Track(track_id=1, zones={'front_door'})
>>> b
Track(track_id=2, zones=set())
```

Each track keeps its own zones. The project's `Track` uses exactly this.

## Learn: dates and times

The `datetime` module has three things you need:

- `datetime` is a date **and** a time of day.
- `time` is only a time of day (`22:00`).
- `timedelta` is a **length** of time (one hour, two days).

```pycon
>>> from datetime import datetime, time, timedelta
>>> now = datetime(2026, 3, 14, 23, 30, 15)
>>> now
datetime.datetime(2026, 3, 14, 23, 30, 15)
>>> now.hour
23
>>> now.minute
30
>>> now.time()
datetime.time(23, 30, 15)
>>> time(22, 0)
datetime.time(22, 0)
>>> now.time() >= time(22, 0)
True
>>> now + timedelta(hours=1)
datetime.datetime(2026, 3, 15, 0, 30, 15)
>>> now - timedelta(days=1)
datetime.datetime(2026, 3, 13, 23, 30, 15)
>>> datetime(2026, 3, 15, 0, 0) - now
datetime.timedelta(seconds=1785)
```

`datetime.now()` gives the current moment (we use fixed dates above so the examples always print the same). To turn a `datetime` into text, use `strftime` or an f-string with the same codes:

```pycon
>>> from datetime import datetime
>>> now = datetime(2026, 3, 14, 23, 30, 15)
>>> now.strftime("%Y-%m-%d %H:%M:%S")
'2026-03-14 23:30:15'
>>> f"{now:%H:%M}"
'23:30'
>>> f"{now:%Y%m%d_%H%M%S}"
'20260314_233015'
>>> now.isoformat(timespec="seconds")
'2026-03-14T23:30:15'
```

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| `%Y` | year (2026) | `%H` | hour, 00-23 |
| `%m` | month (03) | `%M` | minute |
| `%d` | day (14) | `%S` | second |

The project uses these codes to put the time on the video, to name snapshot files (`20261015_195304_person_3.jpg`) and to store events in the database (`isoformat`).

### Two clocks

For **how long something took**, do not use the wall clock. It can jump if the computer changes its time. Use `time.monotonic()`: a number of seconds that only goes up.

```pycon
>>> import time
>>> start = time.monotonic()
>>> time.sleep(0.1)
>>> elapsed = time.monotonic() - start
>>> elapsed >= 0.1
True
>>> type(time.monotonic())
<class 'float'>
```

The project uses `time.monotonic()` for "this person was seen for 12 seconds". (Careful: `time` the **module** and `time` the **class** from `datetime` are different things. In the next files we import the class with `from datetime import time`.)

## Learn: the night rule

"Night" is configured as `["22:00", "06:00"]`. It **crosses midnight**, so a simple `start <= t < end` would never be true (22:00 is not before 06:00). We need two cases:

| Case | Rule |
|---|---|
| Night crosses midnight (`start > end`, like 22:00 to 06:00) | night if `t >= start` **or** `t < end` |
| Night is inside one day (like 01:00 to 05:00) | night if `start <= t < end` |

Check the rule against three times, for 22:00 to 06:00:

| Time | `t >= 22:00` | `t < 06:00` | Night? |
|---|---|---|---|
| 23:30 | yes | no | **yes** |
| 03:00 | no | yes | **yes** |
| 12:00 | no | no | no |

## Lab 5.3: `Detection` and `Track`

Create two files in the `intelligence` package. A `Detection` is what the detector reports for one object in one frame. A `Track` is what the program remembers about one object over many frames (when it first appeared, how many frames it was seen, which zones it entered, how serious it is).

**`intelligence/detector.py`**

```python
from dataclasses import dataclass


@dataclass
class Detection:
    track_id: int
    label: str
    confidence: float
    box: tuple  # x1, y1, x2, y2 in pixels
```

**`intelligence/app.py`**

```python
from dataclasses import dataclass, field


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
```

Check them with a small script. Create `tests/show_dataclasses.py` and run it from the project folder:

**`tests/show_dataclasses.py`**

```python
from intelligence.app import Track
from intelligence.detector import Detection

detection = Detection(track_id=1, label="person", confidence=0.91, box=(47, 400, 239, 904))
print(detection)

a = Track(track_id=1, label="person", first_seen=0.0, last_seen=0.0)
b = Track(track_id=2, label="car", first_seen=0.0, last_seen=0.0)
a.zones.add("front_door")
print(a)
print("b has its own empty set of zones:", b.zones == set())
```

```text
$ python -m tests.show_dataclasses
Detection(track_id=1, label='person', confidence=0.91, box=(47, 400, 239, 904))
Track(track_id=1, label='person', first_seen=0.0, last_seen=0.0, box=(0, 0, 0, 0), frames=0, confirmed=False, zones={'front_door'}, severity=0, alerted_severity=0)
b has its own empty set of zones: True
```

## Lab 5.4 (Milestone 2): The night rule

Create `intelligence/rules.py`. Compared with the skeleton from hour 13:

- `_parse_hm("22:00")` turns text into `time(22, 0)`. (It splits at `:` and converts both parts to numbers.) A name that starts with `_` means "for use inside this file only".
- `__init__` reads `night_hours` from the config and stores both times.
- `is_night(now)` takes a `datetime`, gets its time of day with `.time()`, and applies the two-case rule.

**`intelligence/rules.py`**

```python
from datetime import time


def _parse_hm(text):
    """'22:00' -> datetime.time(22, 0)"""
    hour, minute = text.split(":")
    return time(int(hour), int(minute))


class RuleEngine:
    """Turns "a person is here" into "how much does it matter"."""

    def __init__(self, cfg, store=None):
        self.cfg = cfg
        self.store = store
        self.zones = [z for z in cfg["zones"] if z.get("enabled", True)]
        self.night_start = _parse_hm(cfg["night_hours"][0])
        self.night_end = _parse_hm(cfg["night_hours"][1])

    def is_night(self, now):
        t = now.time()
        if self.night_start > self.night_end:  # spans midnight, e.g. 22:00 -> 06:00
            return t >= self.night_start or t < self.night_end
        return self.night_start <= t < self.night_end
```

Now check it. Create `tests/check_rules.py`. Every `assert` is a case you decided in advance, including the border cases (06:00 exactly is morning, 22:00 exactly is night):

**`tests/check_rules.py`**

```python
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
```

```text
$ python -m tests.check_rules
rules OK
```

If an `assert` fails, Python shows the line. Fix `is_night`, not the test.

## Check yourself

1. Why do we write `zones: set = field(default_factory=set)` and not `zones: set = set()`?
2. How do you turn `datetime(2026, 3, 14, 23, 30)` into the text `20260314_2330`?
3. Why does `22:00 <= t < 06:00` never work for night?
4. Which clock do you use to measure how long a person was in view, and why?

<details><summary>Answers</summary>

1. A default shared by all objects is a bug waiting to happen; `default_factory` makes a fresh set for every object.
2. `f"{when:%Y%m%d_%H%M}"`.
3. No time is both at least 22:00 and before 06:00, because 22:00 is later than 06:00. When the range crosses midnight you need `or` instead.
4. `time.monotonic()`, because it only moves forward and does not jump when the computer's clock changes.

</details>

---

# Hour 15: Git, secrets and Checkpoint 1

## Learn: git

**Git** is a free tool that saves the history of your project. Every **commit** is a snapshot you can return to. It protects you from "it worked yesterday". It also lets a team work together. We use it for two reasons: to save your work, and to **make sure secrets never get saved**.

Install it if `git --version` fails:

| System | How |
|---|---|
| Windows | download "Git for Windows" from `git-scm.com` and accept the default options |
| macOS | run `xcode-select --install` in the terminal |
| Linux | `sudo apt install git` (Ubuntu/Debian) |

Tell git who you are (once per computer):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### The `.gitignore` file

`.gitignore` lists files that git must **never** save. The most important line is `.env`, because it contains your token. The others are files the program creates (snapshots, the database, downloaded models, caches):

**`.gitignore`**

```text
.env
snapshots/
data/
models/
output/
*.mp4
.ultralytics/
__pycache__/
.DS_Store
```

Create this file in your project folder **before** your first commit.

## Lab 5.5: Your first commit

Run these commands in your project folder (the examples below were run on a copy of the project at the end of today, so your output will list your own files):

```text
$ git init
Initialized empty Git repository in /path/to/my-intelligence-system/.git/
```

`git status` shows what git sees. The `??` means "new file that git does not track yet":

```text
$ git status --short
?? .env.example
?? .gitignore
?? config.json
?? exercises/
?? intelligence/
?? security_camera.py
?? tests/
```

Notice what is **not** in the list: `.env`. It is ignored. You can ask git to prove it:

```text
$ git check-ignore -v .env
.gitignore:1:.env	.env
```

The answer says: line 1 of `.gitignore`, the pattern `.env`. Now add everything and make the first commit:

```text
$ git add .
```

```text
$ git commit -q -m "Day 5: config loader, rules, data classes"
```

```text
$ git log --oneline
3f2a9c1 Day 5: config loader, rules, data classes
```

| Command | What it does |
|---|---|
| `git status` | shows changed and new files |
| `git add .` | selects all changes for the next snapshot |
| `git commit -m "message"` | saves the snapshot with a short message |
| `git log --oneline` | lists your snapshots |
| `git diff` | shows what changed since the last commit |

**From now on, commit at the end of every day** with a message like `Day 6: numpy exercises`.

### If a secret is ever committed

Deleting the file in a new commit is **not** enough, because git keeps the old versions. If you commit your token by mistake: open Telegram, talk to **@BotFather**, send `/revoke` and make a new token. Then fix your files. A leaked token must be replaced, not hidden.

(GitHub is a free website where you can store a copy of your repository. It is optional in this course.)

## Checkpoint 1: Python quiz (20 minutes)

Closed book, no running code. One point per question: 15 points.

1. What does `print(7 // 2, 7 % 2, 2 ** 3)` print?
2. What does `f"{'person'.upper()} {0.8734:.2f}"` give?
3. One of these lines has an error. Which one, and why? `if score = 0.5:` or `if score >= 0.5:`
4. Write a function `double(x)` that returns twice `x`. What does `print(double(4))` show?
5. What does `[n * 2 for n in range(4)]` give?
6. For `d = {"a": 1}`: what do `d.get("b", 0)` and `d["b"]` give?
7. What does `{1, 2, 3} & {2, 3, 4}` give?
8. Which is valid JSON? (a) `{'a': 1}` (b) `{"a": 1,}` (c) `{"a": true}`
9. Why do we write `with open(...) as f:`?
10. What does this print?
    ```python
    try:
        int("x")
    except ValueError:
        print("A")
    finally:
        print("B")
    ```
11. Which file turns a folder into a package?
12. In a method, what is `self`?
13. Why `field(default_factory=set)` in a dataclass?
14. What are `datetime(2026, 1, 2, 23, 30).hour` and `time(23, 30) >= time(22, 0)`?
15. Which file lists the files git must never save? Name two commands used to save a snapshot.

<details><summary>Answer key (instructor)</summary>

Code answers computed by Python:

```pycon
>>> print(7 // 2, 7 % 2, 2 ** 3)
3 1 8
>>> f"{'person'.upper()} {0.8734:.2f}"
'PERSON 0.87'
>>> def double(x):
...     return x * 2
...
>>> print(double(4))
8
>>> [n * 2 for n in range(4)]
[0, 2, 4, 6]
>>> d = {"a": 1}
>>> d.get("b", 0)
0
>>> d["b"]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'b'
>>> {1, 2, 3} & {2, 3, 4}
{2, 3}
>>> try:
...     int("x")
... except ValueError:
...     print("A")
... finally:
...     print("B")
...
A
B
>>> from datetime import datetime, time
>>> datetime(2026, 1, 2, 23, 30).hour
23
>>> time(23, 30) >= time(22, 0)
True
```

The other answers:

3. `if score = 0.5:` is the error: a single `=` assigns, and `==` compares.
8. (c) only. JSON uses double quotes and allows no trailing comma.
9. It closes the file automatically, even if an error happens.
11. `__init__.py`.
12. The object the method was called on.
13. So every object gets its own new set instead of all sharing one.
15. `.gitignore`. `git add` and `git commit`.

**Scoring:** 13-15 excellent, 10-12 good, 7-9 revise Days 2-4 this evening, below 7 sit with the student before Day 6.

</details>

---

# Day 5 wrap-up

## Checklist

- [ ] `python -m tests.show_dataclasses` prints a `Detection` and a `Track`.
- [ ] `python -m tests.check_rules` prints `rules OK`.
- [ ] `.gitignore` exists and `git check-ignore -v .env` confirms that `.env` is ignored.
- [ ] You made your first commit.
- [ ] You finished Checkpoint 1.

## Your project folder today

```text
my-intelligence-system/
├── .env                       (ignored by git)
├── .env.example
├── .gitignore                 <- new
├── config.json
├── security_camera.py
├── intelligence/
│   ├── __init__.py
│   ├── config.py
│   ├── rules.py               <- new: RuleEngine, is_night
│   ├── detector.py            <- new: Detection
│   └── app.py                 <- new: Track
├── tests/
│   ├── __init__.py
│   ├── check_config.py
│   ├── check_rules.py         <- new
│   └── show_dataclasses.py    <- new
└── exercises/
    └── day01/ ... day05/
```

Solutions are in [`solutions/day05/`](solutions/day05/).

## Instructor notes

- **`self`** is the big idea of hour 13. Draw two boxes labelled `front` and `garage`, each with its own `name` and `frames_read`, and show that `front.read()` changes only the first box.
- **Do not go deep into OOP.** No inheritance, no properties. Students need: class, `__init__`, `self`, methods, dataclass.
- **Dates:** let students try `strftime` codes themselves; most get the `%m` (month) and `%M` (minute) mix-up once.
- **The night rule** is the first piece of "logic you must reason about". Ask for the border cases (22:00, 06:00) before anyone types code. The `assert` list in `check_rules.py` is the specification.
- **Git** is new to almost everyone. Do the first commit together on the projector. The two lines you must make them repeat: "`.env` is never committed" and "if a token leaks, revoke it".
- **Checkpoint 1:** keep it closed-book and short. Use it to find who needs help before Week 2 (NumPy and OpenCV move faster).
- **If you are behind:** run Lab 5.1 as a demo. Do not skip Labs 5.3-5.4: Days 13-14 use them directly.
- **Fast finishers:** add `__repr__`-free printing of a `RuleEngine`, or write a `Counter` method `percent(label)`.

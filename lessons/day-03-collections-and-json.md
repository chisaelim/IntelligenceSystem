# Day 3: Lists, dictionaries, sets and JSON

**Hours 7-9 of 45** · Project milestone: severity rules that read their numbers from `config.json`

## What you can do at the end of today

- Store many values in **lists** and **tuples**, slice them, and filter them with a list comprehension.
- Store pairs in a **dictionary** and count things with it.
- Use a **set** to keep unique values and to find what is new.
- Read and write **JSON** files, and read the project's `config.json`.
- Upgrade `assess` so it returns the severity **and** the reasons, using a dictionary from the config file.

## Where today fits in the project

A detector does not give you one object. It gives you a **list** of detections for every frame. Each detection has a label, a confidence and a box. Today you practise handling exactly that kind of data.

- **Lists and tuples** hold detections and boxes (Days 7, 12, 13).
- **Dictionaries** hold severities per label, the tracks the camera is following, and every setting (Days 11-15).
- **Sets** keep "which zones has this person already entered?" (Day 14).
- **JSON** is the file format of `config.json`, the control panel of the whole system.

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 7 | 5 | Warm-up: Day 2 exit ticket, question 4 |
| | 15 | Talk: lists, tuples, slicing, comprehensions |
| | 10 | Live demo |
| | 30 | **Lab 3.1** Filter detections |
| 8 | 15 | Talk: dictionaries and sets |
| | 10 | Live demo |
| | 35 | **Labs 3.2-3.4** Count labels, track ids with sets, severity v2 |
| 9 | 15 | Talk: JSON and the structure of `config.json` |
| | 10 | Live demo |
| | 25 | **Labs 3.5-3.6** Read the config, edit the config |
| | 10 | Exit ticket |

---

# Hour 7: Lists and tuples

## Learn

A **list** keeps many values in order. Use square brackets. Items are numbered from **0**:

```pycon
>>> labels = ["person", "car", "dog"]
>>> labels[0]
'person'
>>> labels[-1]
'dog'
>>> labels[0:2]
['person', 'car']
>>> len(labels)
3
>>> labels.append("bus")
>>> labels
['person', 'car', 'dog', 'bus']
>>> "car" in labels
True
>>> labels.remove("dog")
>>> labels
['person', 'car', 'bus']
>>> sorted(labels)
['bus', 'car', 'person']
```

- `labels[-1]` is the last item.
- `labels[0:2]` is a **slice**: from index 0 up to (not including) index 2.
- `sorted()` gives a new sorted list and leaves the original alone.

A **tuple** is like a list that cannot change. Use round brackets. A bounding box is a perfect tuple: four numbers that belong together.

```text
(0,0) ───────────────────────► x
  │        (x1,y1) ┌─────────┐
  │                │ person  │
  ▼ y              └─────────┘ (x2,y2)
```

In an image, `(0, 0)` is the **top-left** corner. `x` grows to the right and `y` grows **downward**. A box is the top-left corner `(x1, y1)` and the bottom-right corner `(x2, y2)`. **Unpacking** puts each value in its own variable:

```pycon
>>> box = (47, 400, 239, 904)
>>> x1, y1, x2, y2 = box
>>> width = x2 - x1
>>> height = y2 - y1
>>> width, height
(192, 504)
>>> box[0] = 5
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment
```

A **list comprehension** builds a new list in one line. Read it as "give me `n * n` for each `n` in `numbers`, but only if...":

```pycon
>>> numbers = [1, 2, 3, 4, 5, 6]
>>> [n * n for n in numbers]
[1, 4, 9, 16, 25, 36]
>>> [n for n in numbers if n % 2 == 0]
[2, 4, 6]
>>> sum(numbers)
21
>>> max(numbers)
6
>>> min(numbers)
1
```

To sort by something other than the item itself, give `sorted` (or `max`) a **key**: a function that says what to sort by. A `lambda` is a tiny one-line function without a name. `lambda p: p[1]` means "given `p`, return `p[1]`":

```pycon
>>> points = [("person", 0.62), ("bus", 0.94), ("person", 0.88)]
>>> sorted(points, key=lambda p: p[1], reverse=True)
[('bus', 0.94), ('person', 0.88), ('person', 0.62)]
>>> max(points, key=lambda p: p[1])
('bus', 0.94)
```

## Lab 3.1: Filter detections

Here is the kind of data a detector produces: one tuple per object, `(label, confidence, (x1, y1, x2, y2))`. These numbers come from a real photo. On Day 12 you will make them yourself.

Create `exercises/day03/detections.py`. Work through the tasks one at a time, run after each one:

1. Keep only detections with confidence at least `0.45` (a comprehension).
2. Count the persons.
3. Make a list with just the labels. (A loop variable can be a whole unpacked tuple: `for label, confidence, box in ...`.)
4. Find the detection with the highest confidence (`max` with a `key`).
5. For every person print the width, the height and the area of its box.
6. Find the three largest boxes (`sorted` with a `key` function and a slice `[:3]`).

**`exercises/day03/detections.py`**

```python
# Each detection is a tuple: (label, confidence, (x1, y1, x2, y2))
detections = [
    ("bus", 0.94, (4, 229, 796, 728)),
    ("person", 0.89, (671, 395, 810, 879)),
    ("person", 0.88, (47, 400, 239, 904)),
    ("person", 0.86, (223, 409, 344, 860)),
    ("person", 0.62, (0, 556, 69, 872)),
    ("person", 0.31, (120, 100, 160, 180)),  # a weak guess
]

MIN_CONFIDENCE = 0.45

# Keep only the confident detections
confident = [d for d in detections if d[1] >= MIN_CONFIDENCE]
print("kept", len(confident), "of", len(detections), "detections")

# Only the persons
persons = [d for d in confident if d[0] == "person"]
print("persons:", len(persons))

# Just the labels
labels = [label for label, confidence, box in confident]
print("labels:", labels)

# The most confident detection
best = max(confident, key=lambda d: d[1])
print("best:", best[0], best[1])

# Size of each person box
for label, confidence, (x1, y1, x2, y2) in persons:
    width = x2 - x1
    height = y2 - y1
    print(f"{label} {confidence:.2f}: width={width}, height={height}, area={width * height:,}")

# The three largest boxes
def box_area(detection):
    x1, y1, x2, y2 = detection[2]
    return (x2 - x1) * (y2 - y1)


largest = sorted(confident, key=box_area, reverse=True)[:3]
print("largest three:", [d[0] for d in largest])
```

```text
$ python exercises/day03/detections.py
kept 5 of 6 detections
persons: 4
labels: ['bus', 'person', 'person', 'person', 'person']
best: bus 0.94
person 0.89: width=139, height=484, area=67,276
person 0.88: width=192, height=504, area=96,768
person 0.86: width=121, height=451, area=54,571
person 0.62: width=69, height=316, area=21,804
largest three: ['bus', 'person', 'person']
```

## Check yourself

1. What is `["a", "b", "c"][1:]`?
2. Why can you change a list but not a tuple?
3. Write a comprehension that gives the confidences of the detections whose label is `"person"`, given `detections` as in the lab.

<details><summary>Answers</summary>

1. `["b", "c"]` (from index 1 to the end).
2. Lists are *mutable* (changeable); tuples are *immutable* by design, which makes them safe for values that belong together, like a box.
3. `[confidence for label, confidence, box in detections if label == "person"]`

</details>

---

# Hour 8: Dictionaries and sets

## Learn

A **dictionary** stores **key: value** pairs. You look up a value by its key instead of a position. The project uses dictionaries for settings, for severities and for the tracks it follows.

```pycon
>>> severity = {"person": 2, "car": 1, "dog": 0}
>>> severity["person"]
2
>>> severity.get("bus", 1)
1
>>> "car" in severity
True
>>> severity["cat"] = 0
>>> len(severity)
4
>>> for label, value in severity.items():
...     print(label, value)
...
person 2
car 1
dog 0
cat 0
>>> severity["bus"]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'bus'
```

- `severity["bus"]` fails with `KeyError` if the key is missing.
- `severity.get("bus", 1)` never fails: it returns the default (`1`) when the key is missing. The project uses this for labels it has no rule for.
- Looping over `.items()` gives you each key and value together.

**Counting pattern.** To count how often each label appears, start with an empty dictionary and add one each time:

```python
counts = {}
for label in sightings:
    counts[label] = counts.get(label, 0) + 1
```

A **set** is a group of **unique** values with no order. Use it to remove duplicates and to ask "is it in there?" very fast. Sets support maths operations:

```pycon
>>> ids = {1, 2, 3}
>>> ids.add(3)
>>> ids.add(4)
>>> ids
{1, 2, 3, 4}
>>> {1, 2, 3} | {3, 4}
{1, 2, 3, 4}
>>> {1, 2, 3} & {3, 4}
{3}
>>> {1, 2, 3} - {3, 4}
{1, 2}
>>> type({})
<class 'dict'>
>>> type(set())
<class 'set'>
```

`|` is union (everything), `&` is intersection (in both), `-` is difference (in the first, not in the second). `{}` is an **empty dictionary**; make an empty set with `set()`.

Sets have no order. When you print a set of text, the order can change from run to run. Use `sorted(my_set)` when you need a stable order.

**Truthiness.** An empty list, tuple, set, dictionary or text counts as `False` in an `if`. A non-empty one counts as `True`. So `if in_zones:` means "if there is at least one zone".

## Lab 3.2: Count sightings

Count how many times each label was seen, and print the most common one.

**`exercises/day03/counting.py`**

```python
sightings = ["person", "car", "person", "dog", "person", "car", "bicycle", "person"]

counts = {}
for label in sightings:
    counts[label] = counts.get(label, 0) + 1

for label, number in counts.items():
    print(f"{label}: {number}")

most_common = max(counts, key=counts.get)
print("most common:", most_common)
```

```text
$ python exercises/day03/counting.py
person: 4
car: 2
dog: 1
bicycle: 1
most common: person
```

## Lab 3.3: Track ids and zones with sets

The tracker gives every object an id. The same id appears in many frames. How many different objects were there? And a person walks from one zone into another: which zone is **new**?

**`exercises/day03/sets_demo.py`**

```python
# Track ids seen in three frames in a row
frame_1 = [1, 2, 3]
frame_2 = [2, 3, 3, 4]  # 3 is listed twice by mistake
frame_3 = [3, 4, 5]

seen = set()
for frame in (frame_1, frame_2, frame_3):
    seen = seen | set(frame)
print("unique track ids:", sorted(seen))

# Which zones is a track in now, and which did it already know about?
known_zones = {"front_door"}
current_zones = {"front_door", "driveway"}
new_zones = current_zones - known_zones
print("new zones:", new_zones)
```

```text
$ python exercises/day03/sets_demo.py
unique track ids: [1, 2, 3, 4, 5]
new zones: {'driveway'}
```

The `new_zones = current_zones - known_zones` line is the same trick the project uses to print a message only the **first** time a person enters a zone.

## Lab 3.4: Severity, version 2

Rebuild `assess` from Day 2 with a dictionary instead of `if/elif` for the base severity, and return the **reasons** as well. Notice the guard clause, `.get` with a default, `in_zones=()` as an empty default, and `", ".join(...)` that turns a list of text into one text.

**`exercises/day03/severity_v2.py`**

```python
LABEL_SEVERITY = {
    "person": 2,
    "car": 1, "truck": 1, "bus": 1, "motorcycle": 1, "bicycle": 1,
    "dog": 0, "cat": 0,
}


def assess(label, at_night=False, in_zones=()):
    """Return (severity, reasons). Severity is 0 to 3."""
    base = LABEL_SEVERITY.get(label, 1)  # unknown labels count as 1
    if base == 0:
        return 0, [label]

    score = base
    reasons = [label]
    if at_night:
        score += 1
        reasons.append("at night")
    if in_zones:
        score += 1
        reasons.append("in " + ", ".join(sorted(in_zones)))
    return min(score, 3), reasons


severity, reasons = assess("person", at_night=True, in_zones={"front_door"})
print(severity, "-", ", ".join(reasons))

severity, reasons = assess("dog", at_night=True)
print(severity, "-", ", ".join(reasons))

severity, reasons = assess("suitcase")
print(severity, "-", ", ".join(reasons))
```

```text
$ python exercises/day03/severity_v2.py
3 - person, at night, in front_door
0 - dog
1 - suitcase
```

Compare with Day 2. The function now says **why** it chose that number. When an alert reaches your phone, the reasons (`person, at night, in front_door`) tell you why it matters.

## Check yourself

1. How do you add one to a count in a dictionary when the key might not exist yet?
2. `{1, 2, 3} - {3}` gives what?
3. What is the difference between `d["x"]` and `d.get("x")` when `"x"` is missing?

<details><summary>Answers</summary>

1. `counts[key] = counts.get(key, 0) + 1`
2. `{1, 2}`
3. `d["x"]` raises a `KeyError`. `d.get("x")` returns `None` (or the default you give).

</details>

---

# Hour 9: JSON and the config file

## Learn

**JSON** is a text format for data. Every programming language can read it, and it is the format of `config.json`. It looks like Python dictionaries and lists, with a few rules:

- Text uses **double quotes** only.
- `true`, `false` and `null` are written in lowercase (Python: `True`, `False`, `None`).
- **No comments** and **no trailing commas**.

```pycon
>>> import json
>>> text = '{"name": "front_door", "enabled": false, "polygon": [[0.1, 0.2], [0.9, 0.2]]}'
>>> zone = json.loads(text)
>>> zone
{'name': 'front_door', 'enabled': False, 'polygon': [[0.1, 0.2], [0.9, 0.2]]}
>>> zone["enabled"]
False
>>> zone["polygon"][0]
[0.1, 0.2]
>>> print(json.dumps(zone, indent=2))
{
  "name": "front_door",
  "enabled": false,
  "polygon": [
    [
      0.1,
      0.2
    ],
    [
      0.9,
      0.2
    ]
  ]
}
```

`json.loads` turns JSON **text** into Python values. `json.dumps` turns Python values into JSON text. For files use `json.load` and `json.dump` (no `s`). To open a file safely, use `with`. It opens the file and closes it automatically when the block ends (Day 4 explains it fully):

```python
with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)
```

If the JSON has a mistake, for example a comma after the last item, Python tells you the line and column:

```text
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 9 (char 8)
```

## The project's `config.json`

Copy `config.json` from the course folder into your project folder (the folder that contains `exercises/`). This one file controls the whole Intelligence System, so you can change how it behaves without touching the code.

**`config.json`**

```json
{
  "source": 0,
  "model": "yolo11n.pt",
  "confidence": 0.45,
  "image_size": 640,
  "device": "auto",

  "watch_classes": ["person", "car", "truck", "bus", "motorcycle", "bicycle", "dog", "cat"],
  "min_track_frames": 5,
  "lost_seconds": 5,

  "label_severity": {
    "person": 2, "car": 1, "truck": 1, "bus": 1, "motorcycle": 1, "bicycle": 1,
    "dog": 0, "cat": 0
  },

  "night_hours": ["22:00", "06:00"],

  "zones": [
    {
      "name": "front_door",
      "enabled": false,
      "polygon": [[0.15, 0.25], [0.85, 0.25], [0.85, 0.95], [0.15, 0.95]],
      "watch": ["person"]
    }
  ],

  "alert": {
    "min_severity": 2,
    "cooldown_seconds": 30
  },

  "anomaly": {
    "enabled": true,
    "min_history": 30,
    "rare_share": 0.02
  },

  "paths": {
    "database": "data/events.db",
    "snapshots": "snapshots",
    "models": "models"
  }
}
```

| Setting | What it controls | Day |
|---|---|---|
| `source` | the camera number (`0`) or a video file | 8 |
| `model`, `confidence`, `image_size`, `device` | the YOLO detector: which model, how sure it must be, input size, CPU or GPU | 12 |
| `watch_classes` | which kinds of objects we care about | 12-13 |
| `min_track_frames`, `lost_seconds` | how long an object must be seen to count, and how long it must be gone to have "left" | 13 |
| `label_severity` | the base severity of each label (0 to 3) | 14 |
| `night_hours` | when "night" starts and ends | 5, 14 |
| `zones` | named areas of the picture (corners are fractions from 0 to 1 of the width and height) | 7, 14 |
| `alert` | the minimum severity that sends a message, and the pause between messages | 14 |
| `anomaly` | the "unusual for this hour" rule | 14 |
| `paths` | where the database, snapshots and model files are kept | 9, 15 |

## Lab 3.5: Read the config

Create `exercises/day03/read_config.py` (run it from the project folder, where `config.json` is). Print the watch list, the night hours, the minimum alert severity, every label with its severity, and the names of the enabled zones.

**`exercises/day03/read_config.py`**

```python
import json

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

print("watching:", ", ".join(cfg["watch_classes"]))
print("night hours:", cfg["night_hours"][0], "to", cfg["night_hours"][1])
print("alert when severity >=", cfg["alert"]["min_severity"])

print("\nSeverity by label:")
for label, severity in cfg["label_severity"].items():
    print(f"  {label:10} {severity}")

enabled = [z["name"] for z in cfg["zones"] if z["enabled"]]
print("\nenabled zones:", enabled if enabled else "none")
```

```text
$ python exercises/day03/read_config.py
watching: person, car, truck, bus, motorcycle, bicycle, dog, cat
night hours: 22:00 to 06:00
alert when severity >= 2

Severity by label:
  person     2
  car        1
  truck      1
  bus        1
  motorcycle 1
  bicycle    1
  dog        0
  cat        0

enabled zones: none
```

Notice `f"  {label:10} {severity}"`. The `:10` pads the label to 10 characters so the numbers line up in a column.

## Lab 3.6: Change the config from Python

Read the config, change two values, and save it to a **new** file (never overwrite your real config while learning).

**`exercises/day03/edit_config.py`**

```python
import json

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

cfg["alert"]["min_severity"] = 3
cfg["zones"][0]["enabled"] = True

with open("config_test.json", "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
print("saved config_test.json")

with open("config_test.json", encoding="utf-8") as f:
    check = json.load(f)
print("min_severity is now", check["alert"]["min_severity"])
print("front_door enabled:", check["zones"][0]["enabled"])
```

```text
$ python exercises/day03/edit_config.py
saved config_test.json
min_severity is now 3
front_door enabled: True
```

## Lab 3.7: Severity from the config

Now connect everything. Instead of typing the severities in your code, read them from `config.json`. Change one number in `config.json` (for example make `bus` `2`), run again, and see that the code did not need to change. This is the point of a config file.

**`exercises/day03/severity_from_config.py`**

```python
import json

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

LABEL_SEVERITY = cfg["label_severity"]  # the dictionary now comes from the file


def assess(label, at_night=False, in_zones=()):
    """Return (severity, reasons). Severity is 0 to 3."""
    base = LABEL_SEVERITY.get(label, 1)
    if base == 0:
        return 0, [label]

    score = base
    reasons = [label]
    if at_night:
        score += 1
        reasons.append("at night")
    if in_zones:
        score += 1
        reasons.append("in " + ", ".join(sorted(in_zones)))
    return min(score, 3), reasons


for label in ("person", "bus", "cat"):
    severity, reasons = assess(label, at_night=True)
    print(f"{label:7} at night -> {severity} ({', '.join(reasons)})")
```

```text
$ python exercises/day03/severity_from_config.py
person  at night -> 3 (person, at night)
bus     at night -> 2 (bus, at night)
cat     at night -> 0 (cat)
```

## Check yourself (exit ticket)

1. Name two differences between JSON and Python dictionaries.
2. What is `cfg["zones"][0]["name"]`? Read it from left to right.
3. Why is the severity table in a file and not in the code?
4. Which structure would you use for: (a) the corners of one box, (b) the number of times each label was seen, (c) the track ids seen so far?

<details><summary>Answers</summary>

1. JSON uses double quotes only, `true/false/null` in lowercase, and allows no comments or trailing commas. (Python also allows single quotes, `True/False/None`, and comments.)
2. Take `cfg`, then the item called `"zones"` (a list), then its first element `[0]` (a dictionary), then its `"name"`: `"front_door"`.
3. So you can change the behaviour (and so can a non-programmer) without editing and re-testing the code, and without a new version of the program.
4. (a) a tuple, (b) a dictionary, (c) a set.

</details>

## Homework (optional, 20 minutes)

Given a list of `(label, confidence)` pairs, group the confidences by label and print, for each label, how many detections there were and the average confidence. Hint: a dictionary whose values are lists.

<details><summary>Solution</summary>

**`exercises/day03/summary.py`**

```python
detections = [("person", 0.9), ("car", 0.8), ("person", 0.7), ("person", 0.5), ("car", 0.6)]

# Group the confidences by label: {"person": [0.9, 0.7, 0.5], "car": [0.8, 0.6]}
groups = {}
for label, confidence in detections:
    if label not in groups:
        groups[label] = []
    groups[label].append(confidence)

for label, values in groups.items():
    average = sum(values) / len(values)
    print(f"{label}: {len(values)} detections, average confidence {average:.2f}")
```

```text
$ python exercises/day03/summary.py
person: 3 detections, average confidence 0.70
car: 2 detections, average confidence 0.70
```

</details>

---

# Day 3 wrap-up

## Checklist

- [ ] `detections.py` runs and prints the same numbers as above.
- [ ] `counting.py`, `sets_demo.py` and `severity_v2.py` run.
- [ ] `config.json` is in your project folder and `read_config.py` prints its settings.
- [ ] `severity_from_config.py` works, and it still works after you change a severity in the file.
- [ ] You can explain `.get(key, default)`.

## Your project folder today

```text
my-intelligence-system/
├── config.json              <- copied from the course folder
└── exercises/
    ├── day01/ ...
    ├── day02/ ...
    └── day03/
        ├── detections.py
        ├── counting.py
        ├── sets_demo.py
        ├── severity_v2.py
        ├── read_config.py
        ├── edit_config.py
        ├── severity_from_config.py
        └── summary.py   (homework)
```

Solutions are in [`solutions/day03/`](solutions/day03/).

## Instructor notes

- **Slicing and index numbers** are the hardest part of hour 7. Draw the list on the board with indexes above and below (`0 1 2` and `-3 -2 -1`).
- **Do not rush the comprehension.** Write the same task twice: once with a `for` loop and `append`, then as a comprehension. Students need to see they are the same thing.
- **Lambda** is only a tool for `key=`. Say "you will not write many of these" and move on.
- **Dictionary vs set confusion:** `{}` is an empty dictionary. Make students run `type({})`.
- **Typical mistakes:** modifying a list while looping over it; forgetting that `sorted()` returns a new list; `KeyError` from `d["x"]`; opening `config.json` from a folder where it does not exist (`FileNotFoundError`, the working folder matters, which Day 4 explains).
- **Where is `config.json`?** If a student sees `FileNotFoundError: config.json`, they ran the script from the wrong folder. Always run scripts from the project folder: `python exercises/day03/read_config.py`.
- **Fast finishers:** write a function that returns only the detections inside a zone (given as `x1, y1, x2, y2`).

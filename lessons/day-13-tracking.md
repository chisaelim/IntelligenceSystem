# Day 13: Tracking

**Hours 37-39 of 45** · **Milestone 7:** `intelligence/detector.py` (YOLO detection and tracking) and the loop that notices when something **appears** and **leaves**

## What you can do at the end of today

- Explain why detection alone is not enough, and what a tracker adds.
- Use YOLO's built-in tracker (ByteTrack) and read the track ids.
- Write the `Detector` class that hides the library behind a simple `track(frame)` method.
- Keep one `Track` object per followed object, and decide when it has **appeared** and when it has **left**.
- Run your camera program and see "person #3 appeared ... left after 12s" on live video.

## Where today fits in the project

The detector from Day 12 looks at every frame **alone**. It does not know that the person in frame 12 is the same person as in frame 11. Without that:

- you cannot say **how long** someone has been in the picture;
- you cannot say "this person **just entered** the zone";
- you would send **one alert per frame** (30 per second!) instead of one alert per person.

A **tracker** gives every object an **id** that stays the same from frame to frame. Today you add it, and you build the part of the program that turns a stream of detections into **events**: *appeared* and *left*.

```text
frame → YOLO detections → tracker (ids) → Track objects → "person #3 appeared" / "person #3 left after 12s"
                                                            (rules and alerts come on Day 14 and 15)
```

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 37 | 5 | Warm-up: what does IoU measure? |
| | 20 | Talk: tracking, ByteTrack, ids |
| | 35 | **Lab 13.1** Track ids on your clip |
| 38 | 15 | Talk: designing the `Detector` class |
| | 45 | **Lab 13.2 (Milestone 7)** Write `detector.py` and test it |
| 39 | 15 | Talk: the life of a track: new, confirmed, lost |
| | 45 | **Lab 13.3** Put the detector and the track bookkeeping into the camera loop |

---

# Hour 37: Tracking

## Learn

Look at two consecutive frames. Both have a "person" box. Is it the same person? A human says "of course, it is in nearly the same place". A tracker does the same thing with numbers:

1. **Predict.** For each person tracked so far, guess where the box will be in the new frame (it was moving right, so it will be a bit more to the right).
2. **Match.** Compare the new detections with the predicted boxes using **IoU** (Day 12). A new box that overlaps a predicted box a lot is the same object. The best overall pairing of boxes and tracks is a classic problem called the **assignment problem**. The package `lap` that is in our environment solves it quickly. This is why `lap` is installed: the tracker needs it.
3. **Update.** A matched track takes the new box and keeps its **id**.
4. **New and lost.** A detection that matches nothing starts a **new track** with a new id. A track that matches nothing is marked **lost**. The tracker keeps it for a short while (about one second) in case the object comes back, then forgets it.

Our tracker is **ByteTrack**, which comes with `ultralytics`. Its clever idea: besides the confident boxes it also uses the *weak* boxes (low confidence), because a person who is half hidden behind a pillar often gets a weak box, and that weak box can keep the track alive.

In `ultralytics` you track with one call:

```python
results = model.track(frame, persist=True, tracker="bytetrack.yaml", conf=0.45, classes=[0])
```

| Option | Meaning |
|---|---|
| `persist=True` | **Keep the tracker's memory between calls.** When you give frames one at a time (a webcam loop), this is essential. Without it every call starts a new tracker and ids restart at 1. |
| `tracker="bytetrack.yaml"` | choose ByteTrack |
| `conf` | the confidence threshold, as on Day 12 |
| `classes=[0]` | track only these class numbers (`0` is `person`) |

**A trap.** When nothing is being tracked, `result.boxes.id` is **`None`**, not an empty list. Code that does `result.boxes.id.int()` crashes on every empty frame. Always check for `None` first.

## Lab 13.1: Track ids on your clip

Create `exercises/day13/track_ids.py`. It tracks the persons in a video and prints the ids found in one frame out of every 10. It also counts how many different ids were seen.

**`exercises/day13/track_ids.py`**

```python
import sys

from ultralytics import YOLO

source = sys.argv[1] if len(sys.argv) > 1 else "clip.mp4"
model = YOLO("models/yolo11n.pt")

all_ids = set()
results = model.track(source, stream=True, persist=True, tracker="bytetrack.yaml",
                      conf=0.45, classes=[0], verbose=False)  # classes=[0]: persons only
for frame_number, result in enumerate(results):
    # When nothing is being tracked, result.boxes.id is None (not an empty list!)
    ids = [] if result.boxes.id is None else result.boxes.id.int().tolist()
    all_ids.update(ids)
    if frame_number % 10 == 0:
        print(f"frame {frame_number:3d}: track ids {ids}")

print("different persons seen:", len(all_ids), sorted(all_ids))
```

Run it on **your clip** from Day 8. The output below is from the sample clip (the bus photo that slowly drifts out of the picture) so that you can see what to look for:

```bash
python exercises/day13/track_ids.py clip.mp4
```

```text
$ python exercises/day13/track_ids.py clip.mp4
frame   0: track ids [1, 2, 3, 4]
frame  10: track ids [1, 2, 3, 4]
frame  20: track ids [1, 2, 3]
frame  30: track ids [1, 2, 3, 4]
frame  40: track ids [2, 3]
frame  50: track ids []
frame  60: track ids []
different persons seen: 4 [1, 2, 3, 4]
```

Read the output:

- Four persons were seen and they kept the **same ids** (`1, 2, 3, 4`) for the whole clip, even while they moved.
- In frame 20 person `4` was missing for a moment (it was not detected in that frame), yet in frame 30 it is **back with the same id 4**. The tracker remembered it. That is the benefit of tracking.
- Frame 50 and 60 show `[]`: everyone has left.

Your own clip should show **your** id, probably `1`. If you left the picture and came back, did you get the same id or a new one?

**Experiment:** run it on your clip and answer: (a) What happens to your id if you leave the picture for 10 seconds and then come back? (b) What happens if you only step out for half a second? A new id after a long absence is normal: from the program's point of view, a tracker follows **continuous presence**, not people's identity. It does not recognise faces.

## Check yourself

1. Why does `persist=True` matter when you process one frame at a time?
2. What does the tracker do with a detection that overlaps no existing track?
3. What is `result.boxes.id` when nothing is tracked?
4. Does a tracker know who a person is?

<details><summary>Answers</summary>

1. It keeps the tracker's memory (the tracks and their ids) between calls. Without it, every call starts from zero and every person gets a new id every frame.
2. It starts a new track with a new id.
3. `None`. Check for it before using the ids.
4. No. It only knows that two boxes in consecutive frames are probably the same object, using position and overlap.

</details>

---

# Hour 38: The `Detector` class (Milestone 7)

## Learn: why wrap the library?

You could call `model.track(...)` directly in the camera loop. But the loop would then be full of `ultralytics` details (`boxes.xyxy`, `.int().tolist()`, `None` checks). A cleaner design is a small class, `Detector`, with **one** method, `track(frame)`, that returns a plain list of `Detection` objects (the dataclass you wrote on Day 5). The rest of the program then knows nothing about YOLO. Benefits: simpler code, easy to test, and you could replace YOLO with something else later without touching the loop.

```text
camera loop  ──frame──►  Detector.track()  ──► [Detection, Detection, ...]
                           (YOLO + ByteTrack hidden inside)
```

## Lab 13.2 (Milestone 7): Write `detector.py`

Open `intelligence/detector.py`. Keep your `Detection` dataclass from Day 5 and add the rest. Here is the complete file:

**`intelligence/detector.py`**

```python
from dataclasses import dataclass

import torch
from ultralytics import SETTINGS, YOLO

# No anonymous usage analytics from ultralytics.
try:
    SETTINGS.update(sync=False)
except Exception:
    pass


@dataclass
class Detection:
    track_id: int
    label: str
    confidence: float
    box: tuple  # x1, y1, x2, y2 in pixels


def pick_device(preference="auto"):
    if preference != "auto":
        return preference
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class Detector:
    """YOLO object detection with ByteTrack so each object keeps a stable ID."""

    def __init__(self, model_path, watch_classes, confidence, image_size, device="auto"):
        self.model = YOLO(str(model_path))
        self.device = pick_device(device)
        self.confidence = confidence
        self.image_size = image_size

        names = self.model.names  # {class_id: name}
        unknown = [c for c in watch_classes if c not in names.values()]
        if unknown:
            raise ValueError(f"Unknown class names in watch_classes: {unknown}")
        self.class_ids = [i for i, n in names.items() if n in watch_classes]

    def track(self, frame):
        result = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=self.class_ids,
            conf=self.confidence,
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )[0]
        boxes = result.boxes
        if boxes is None or boxes.id is None:
            return []
        names = result.names
        detections = []
        for xyxy, tid, cls, conf in zip(
            boxes.xyxy.tolist(), boxes.id.int().tolist(), boxes.cls.int().tolist(), boxes.conf.tolist()
        ):
            detections.append(Detection(tid, names[cls], conf, tuple(xyxy)))
        return detections
```

Walk through it:

**The imports and settings.** `SETTINGS.update(sync=False)` switches off the library's anonymous usage statistics. It sits in `try/except` because a settings problem must never stop the program.

**`pick_device`** is the function from Day 12: respect an explicit choice, otherwise use `cuda`, then `mps`, then `cpu`.

**`Detector.__init__`** receives everything it needs as arguments, which are exactly the values from `config.json`:

- it loads the model: `YOLO(str(model_path))` (downloads it the first time);
- it picks the device;
- it turns the **names** in `watch_classes` (`"person"`, `"car"`...) into the model's class **numbers**. First it checks that every name exists. A typo like `"persn"` raises a `ValueError` at start-up with a clear message instead of silently watching nothing. The list `self.class_ids` is then given to YOLO, so it does not even look for other objects (faster, and no wasted detections).

**`Detector.track(frame)`**:

1. Calls `self.model.track(...)` with all the options from the config (`persist=True`, ByteTrack, the classes, the confidence, the image size, the device, `verbose=False`).
2. `[0]` takes the result for our single frame.
3. If there are no boxes, or `boxes.id is None`, return an empty list.
4. Otherwise `zip` walks over four lists at once: the boxes, the ids, the class numbers and the confidences. `.tolist()` turns tensors into plain Python lists and `.int()` makes the ids and classes whole numbers. For each object it builds one `Detection`.

## The test

Create `tests/check_detector.py`. It checks: that `pick_device` respects a choice, that a wrong class name is rejected, that the bus photo gives a bus and at least three persons, that the results obey the config (`watch_classes`, `confidence`), that every object has its own id, that **the same picture again gives the same ids** (tracker memory), and that a **grey picture** gives `[]` without crashing:

**`tests/check_detector.py`**

```python
import cv2
import numpy as np
from ultralytics.utils import ASSETS

from intelligence.config import load_config, project_path
from intelligence.detector import Detection, Detector, pick_device

cfg = load_config()

assert pick_device("cpu") == "cpu"  # a choice you make is respected
assert pick_device("auto") in ("cpu", "cuda", "mps")

model_path = project_path(cfg["paths"]["models"]) / cfg["model"]
detector = Detector(model_path, cfg["watch_classes"], cfg["confidence"], cfg["image_size"], "cpu")

# A class name the model does not know is reported at once, not silently ignored
try:
    Detector(model_path, ["person", "unicorn"], 0.45, 640, "cpu")
    raise AssertionError("an unknown class name should be rejected")
except ValueError as error:
    assert "unicorn" in str(error)

# A real photo: several persons and a bus
frame = cv2.imread(str(ASSETS / "bus.jpg"))
detections = detector.track(frame)
assert detections, "nothing found in the bus photo"
assert all(isinstance(d, Detection) for d in detections)
labels = [d.label for d in detections]
assert "bus" in labels and labels.count("person") >= 3, labels
assert all(d.label in cfg["watch_classes"] for d in detections)
assert all(d.confidence >= cfg["confidence"] for d in detections)
ids = [d.track_id for d in detections]
assert len(set(ids)) == len(ids), "every object needs its own track id"

# The same picture again: the tracker (persist=True) keeps the same ids
again = detector.track(frame)
assert sorted(d.track_id for d in again) == sorted(ids), "ids should stay the same for the same picture"

# A grey picture: nothing found, and the code must not crash on "no ids"
assert detector.track(np.full_like(frame, 114)) == []

print("detector OK")
```

```text
$ python -m tests.check_detector
detector OK
```

The first run is slow because PyTorch is loading. If you see `detector OK`, Milestone 7 is done.

## Check yourself

1. Why does `Detector.__init__` check the class names?
2. What does `track` return when nothing is found?
3. Why does the rest of the program only use `Detection` and not YOLO's own result objects?

<details><summary>Answers</summary>

1. To catch a typo (like `"persn"`) at start-up with a clear error, instead of a program that silently watches nothing.
2. An empty list `[]`.
3. To keep the program simple and independent of the library. Only `detector.py` needs to know how YOLO works, which also makes testing and later changes easier.

</details>

---

# Hour 39: The life of a track

## Learn

The `Detector` gives us **detections**: what is in this frame. The program also needs **tracks**: what it *remembers*. For every id it keeps one `Track` object (Day 5) in a dictionary, `tracks = {id: Track}`. On every frame:

1. **For each detection:** find its track by id. If there is none, create one (`first_seen = now`). Update `last_seen`, `box` and the counter `frames`.
2. **Confirm.** A track is not "real" until it has been seen in at least `min_track_frames` frames (5 in `config.json`). This is a **filter against flicker**: a reflection, a shadow or a wrong detection often lasts only 1 or 2 frames. When the counter reaches 5, the track becomes `confirmed` and the program says **appeared**.
3. **Lost.** A track that was not seen in this frame is checked: if more than `lost_seconds` (5) have passed since `last_seen`, the object has **left**: say so, and remove the track. The 5 seconds avoid "left, appeared, left, appeared" when the detector misses someone for a moment.

```text
        first detection          seen in 5 frames           not seen for > 5 s
   ──────────► NEW (unconfirmed) ───────────► CONFIRMED ────────────────────► LEFT (removed)
                    │  gone too soon (flicker)                                  
                    └──────────► forgotten silently (never announced)
```

**Why seconds and not frames?** A webcam may run at 30 frames per second or at 8 when it is slow. "5 seconds" means the same thing on every computer. Frames would not. So for time we use the **monotonic clock** (`time.monotonic()`, Day 5), which measures how much time passed and never jumps backwards.

**One more point.** We cannot remove items from a dictionary **while looping over it**. So the code first collects the ids to remove in a list, then removes them in a second loop.

**A note about video files.** A computer processes a file much faster than real time (65 frames in about one second). In that single second nobody can be "unseen for 5 seconds", so tracks do not become `lost` while the file runs. They are all closed at the end, when the program shuts down (`finally`). With a **webcam** it works in real time.

## Lab 13.3: Detector and tracks in the camera loop

Update `intelligence/app.py`. These are the changes compared with Day 8:

1. Import `project_path` and create the `Detector` inside `main()` (an import inside a function is fine here: loading PyTorch takes several seconds, so we do it only when we really need it).
2. Keep a dictionary `tracks`.
3. In the loop: call `detector.track(frame)`, update or create tracks, confirm them, find the lost ones.
4. The `finally` block closes all remaining tracks.
5. The old `print("Read N frames")` is gone.

Here is the complete file:

**`intelligence/app.py`**

```python
import argparse
import time
from dataclasses import dataclass, field
from datetime import datetime

import cv2

from .config import load_config, project_path
from .rules import RuleEngine

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
    rules = RuleEngine(cfg)

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
    tracks = {}  # track id -> Track

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
                    print(f"[{now:%H:%M:%S}] {t.label} #{t.track_id} appeared")

            # A track that has not been seen for a while has left.
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
```

Read the loop carefully. Everything between `for det in detector.track(frame):` and `finish_track(tracks.pop(tid))` is the track life cycle you just learned:

- `seen_ids` collects the ids seen in this frame. The lost check uses it: `tid not in seen_ids`.
- `tracks.get(det.track_id)` gives `None` when the id is new. Then `Track(det.track_id, det.label, clock, clock)` creates it with `first_seen = last_seen = clock`.
- `t.last_seen, t.box, t.label = clock, det.box, det.label` is three assignments in one line.
- `finish_track(t)` prints how long the object was seen: `t.last_seen - t.first_seen`. Only `confirmed` tracks are announced, so flickers stay silent.
- The overlay is drawn only when there is a window. It draws the tracks seen in this frame, as before.

Run it on the sample clip, without a window. You will see the five objects (the bus and four persons) appear and then "leave" at the end, when the file is finished:

```text
$ python security_camera.py --source clip.mp4 --no-window
Loading yolo11n.pt ...
Running on mps. Press q to quit.
[20:42:55] bus #1 appeared
[20:42:55] person #2 appeared
[20:42:55] person #3 appeared
[20:42:55] person #4 appeared
[20:42:55] person #5 appeared
[20:42:56] bus #1 left after 1s
[20:42:56] person #2 left after 1s
[20:42:56] person #3 left after 1s
[20:42:56] person #4 left after 1s
[20:42:56] person #5 left after 1s
```

(The first line, `Loading yolo11n.pt ...`, and the device in `Running on ...` can differ on your computer. The times of day are your own.)

Now the real thing, with your webcam and the window. Walk into the picture, stand for a while, and walk out:

```bash
python security_camera.py
```

You should see: a **grey box** with `person #1` (grey because we have no severity yet, that is Day 14), and in the terminal `[14:03:07] person #1 appeared` shortly after you enter, and `[14:03:19] person #1 left after 12s` **about 5 seconds after you left the picture** (because of `lost_seconds`).

**Experiments** (change `config.json`, run again, and explain what you see):

1. `"min_track_frames": 1` and then `30`. How does the moment of "appeared" change? Which setting makes more false "appeared" lines?
2. `"lost_seconds": 1` and then `15`. What happens when you step out and back in after 3 seconds?
3. `"confidence": 0.8`. Do you still appear?
4. `"watch_classes": ["person"]`. What disappears?

## Keep the old tests working

Behaviour changed (the program loads the detector and no longer prints a frame count), so the Day 8 test `tests/check_app.py` must change too. This is normal: **when you change behaviour on purpose, update the test on purpose.** Replace it with this version:

**`tests/check_app.py`**

```python
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

from intelligence.app import parse_source

# parse_source: a camera number becomes an int, a file name stays text
assert parse_source("0") == 0
assert parse_source(2) == 2
assert parse_source("clip.mp4") == "clip.mp4"

# Make a tiny video of 10 grey frames and run the whole program on it, without a window
Path("output").mkdir(exist_ok=True)
writer = cv2.VideoWriter("output/tiny.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 10, (160, 120))
for i in range(10):
    writer.write(np.full((120, 160, 3), 20 * i, np.uint8))
writer.release()

result = subprocess.run(
    [sys.executable, "security_camera.py", "--source", "output/tiny.mp4", "--no-window"],
    capture_output=True, text=True,
)
assert result.returncode == 0, result.stderr
assert "Running on" in result.stdout, result.stdout  # the detector was loaded and the loop ran
assert "appeared" not in result.stdout  # a grey picture has no objects in it

# A source that does not exist gives a friendly message, not a traceback
result = subprocess.run(
    [sys.executable, "security_camera.py", "--source", "no_such_file.mp4", "--no-window"],
    capture_output=True, text=True,
)
assert result.returncode != 0
assert "Cannot open source" in result.stderr, result.stderr
assert "Traceback" not in result.stderr, result.stderr

print("app OK")
```

Add a new test that runs the **whole pipeline** (video, detector, tracks, events) on a short video built from the bus photo, and checks that every object that appeared also left:

**`tests/check_pipeline.py`**

```python
import subprocess
import sys
from pathlib import Path

import cv2
from ultralytics.utils import ASSETS

# A short video made from one photo: 12 identical frames
Path("output").mkdir(exist_ok=True)
frame = cv2.imread(str(ASSETS / "bus.jpg"))
height, width = frame.shape[:2]
writer = cv2.VideoWriter("output/bus_clip.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 10, (width, height))
for _ in range(12):
    writer.write(frame)
writer.release()

result = subprocess.run(
    [sys.executable, "security_camera.py", "--source", "output/bus_clip.mp4", "--no-window"],
    capture_output=True, text=True,
)
assert result.returncode == 0, result.stderr

lines = result.stdout.splitlines()
appeared = [line for line in lines if " appeared" in line]
left = [line for line in lines if " left after" in line]
assert any("bus" in line for line in appeared), result.stdout
assert sum("person" in line for line in appeared) >= 3, result.stdout
assert len(left) == len(appeared), "every object that appeared must also be reported as left"

print(f"pipeline OK: {len(appeared)} objects appeared and left")
```

```text
$ python -m tests.check_app
app OK
```

```text
$ python -m tests.check_pipeline
pipeline OK: 5 objects appeared and left
```

If both pass, Milestone 7 and the track life cycle are done.

## Check yourself (exit ticket)

1. Why does a track need to be seen in several frames before it is "confirmed"?
2. Why do we measure `lost_seconds` in seconds, not in frames?
3. What happens to a track whose object stays in the picture for the whole video?
4. In the loop, why do we collect the lost ids in a list before removing them?

<details><summary>Answers</summary>

1. To ignore flicker: a wrong or short detection (a reflection, a shadow) usually lasts only a frame or two, and should not create an event.
2. Seconds mean the same on every computer. The number of frames per second changes with the camera and the speed of the computer.
3. It is never "lost" during the run. It is closed when the program shuts down (`finally`), and "left after Ns" is printed then.
4. Python does not allow changing a dictionary while you loop over it. We first decide **which** to remove, then remove them.

</details>

## Homework (optional, 30 minutes)

Record a second clip with **two people** who cross each other. Run `track_ids.py` on it. Do the ids stay with the same people? When two people overlap, an **id switch** can happen. Write two sentences about what you saw and why you think it happens (hint: think about IoU).

---

# Day 13 wrap-up

## Checklist

- [ ] `track_ids.py` shows stable ids on your clip.
- [ ] `python -m tests.check_detector` prints `detector OK`.
- [ ] `python -m tests.check_app` prints `app OK` and `python -m tests.check_pipeline` prints `pipeline OK`.
- [ ] On your webcam, `python security_camera.py` prints "appeared" and, about five seconds after you leave, "left after Ns".
- [ ] You changed `min_track_frames` and `lost_seconds` and explained the effect.
- [ ] You committed (`git commit -m "Day 13: detector and track life cycle"`).

## Your project folder today

```text
my-intelligence-system/
├── intelligence/
│   ├── detector.py             <- complete: pick_device, Detector
│   ├── app.py                  <- detector and tracks in the loop
│   └── ...
├── tests/
│   ├── check_detector.py       <- new
│   ├── check_app.py            <- updated
│   ├── check_pipeline.py       <- new
│   └── ...
└── exercises/day13/
    └── track_ids.py
```

Solutions are in [`solutions/day13/`](solutions/day13/): the exercise files directly in the folder, and the project files in [`project/`](solutions/day13/project/).

## Instructor notes

- **Tracking is easier to understand with two hands.** Ask two students to walk past each other in front of the projector and show the ids on screen. Let the class predict whether the ids will switch.
- **`persist=True`:** if a student forgets it, ids restart at 1 every frame and nothing is ever "confirmed". It is the most common bug today.
- **`boxes.id is None`:** the `Detector` handles it, but students writing `track_ids.py` will meet it. Let the crash happen once.
- **Wait for 5 seconds:** many students think "left" is broken because nothing prints when they leave. Explain `lost_seconds` before they test.
- **Speed:** if the preview is slow (under 8 frames per second), lower `image_size` to 480 or 320 in `config.json`, or check that the device is the GPU (`Running on mps` / `cuda`).
- **Webcam in a dark room:** low light lowers confidence, so a person may not reach `0.45`. Turn the light on, or lower `confidence` for the test.
- **If you are behind:** use the sample `clip.mp4` and skip the experiments. Milestone 7 (`detector.py` and its test) and the loop (Lab 13.3) are needed on Day 14.
- **Fast finishers:** print how many frames per second the loop runs (count frames and divide by elapsed time, like Day 8), or show the track id and the time since `first_seen` on the video.

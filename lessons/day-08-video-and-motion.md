# Day 8: Video and motion

**Hours 22-24 of 45** · **Milestone 4:** the camera loop (`security_camera.py --source ... --no-window`), your own test video, and a motion detector

## What you can do at the end of today

- Open a webcam or a video file and read it frame by frame.
- Fix the usual camera problems (permission, wrong camera number).
- Give your program command-line options with `argparse`.
- Measure speed (frames per second) and save timestamped snapshots.
- Build a classic **motion detector** and explain why it is not enough.
- Record your own short video that you will use on Days 12-15.

## Where today fits in the project

The Intelligence System starts with a **loop that reads the camera**: get a frame, look at it, repeat. Everything else is added inside that loop: detection (Day 13), rules (Day 14), alerts (Day 15). Today you build the loop and the way to start it (`python security_camera.py --source clip.mp4`). You also build the old way to detect something happening, a motion detector, so that on Day 12 you can see exactly what AI gives you that this method cannot.

```text
                 ┌────────── the loop you build today ──────────┐
 camera / file → read frame → draw overlay → show window → key "q"? ─┐
                      ▲                                              │ no
                      └──────────────────────────────────────────────┘
```

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 22 | 5 | Warm-up: how do you make a colour picture brighter safely? |
| | 15 | Talk: video, frames, `VideoCapture`, camera permissions |
| | 10 | Live demo |
| | 30 | **Lab 8.1** Live view and camera info |
| 23 | 15 | Talk: `argparse`, FPS, timestamps |
| | 10 | Live demo |
| | 35 | **Labs 8.2-8.4 (Milestone 4)** Snapshots, the project loop, record your clip |
| 24 | 15 | Talk: how motion detection works |
| | 10 | Demo with the test video |
| | 35 | **Labs 8.5-8.6** Compare two methods, try it on your camera |

---

# Hour 22: Reading video

## Learn

A video is many pictures (**frames**) shown quickly. **FPS** (frames per second) says how many. Each frame is a NumPy array, so everything from Days 6 and 7 works on a frame.

`cv2.VideoCapture` opens a video source. The source is either a **number** (the camera: `0` is the first camera, `1` the second) or a **file name**:

```python
cap = cv2.VideoCapture(0)            # the first webcam
cap = cv2.VideoCapture("clip.mp4")   # a video file

ok, frame = cap.read()               # ok is True if we got a frame
```

| Call | Meaning |
|---|---|
| `cap.isOpened()` | `False` if the camera or file could not be opened (no exception is raised!) |
| `ok, frame = cap.read()` | the next frame. `ok` is `False` when there is no frame |
| `cap.get(cv2.CAP_PROP_FPS)` | speed of the video (also `CAP_PROP_FRAME_WIDTH`, `_HEIGHT`, `_FRAME_COUNT`) |
| `cap.release()` | give the camera back to the system |

**What does `ok == False` mean?** For a **video file** it means "the video is finished". For a **webcam** it means "trouble": try again in a moment. The project's loop handles both cases.

**The quit key.** `cv2.waitKey(1)` returns the code of the key that was pressed (or `-1`). `& 0xFF` keeps the last 8 bits, which makes the code the same on every system. `ord("q")` is the code of the letter `q`. So `cv2.waitKey(1) & 0xFF == ord("q")` means "the user pressed q".

### Camera problems

| System | What to check |
|---|---|
| macOS | The first time, macOS asks for camera access for the app that runs Python (**Terminal**, **VS Code**...). If you clicked "Don't allow": System Settings > Privacy & Security > Camera, and switch the app on. Restart the app. If you have an iPhone nearby, "Continuity Camera" may be camera `0`: try `1`. |
| Windows | Settings > Privacy & security > Camera: switch on "Camera access" and "Let desktop apps access your camera". Close Zoom/Teams (they can hold the camera). The first open can be slow; the project sets a setting to make it faster. |
| Linux | Check `ls /dev/video*`. Your user must be in the `video` group (`groups` shows it). |
| All | `cv2.VideoCapture(1)` if camera `0` is a virtual or phone camera. Only one program can use a camera at a time. |

## Lab 8.1: Live view and camera info

Create `exercises/day08/live_view.py`. It shows your webcam until you press `q`.

**`exercises/day08/live_view.py`**

```python
import os

# Windows: faster webcam start. This must be set BEFORE cv2 is imported.
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2

cap = cv2.VideoCapture(0)  # 0 = the first camera
if not cap.isOpened():
    raise SystemExit("Cannot open the camera. Check the camera permission and the camera number.")

print("Press q in the video window to quit.")
while True:
    ok, frame = cap.read()
    if not ok:
        print("No frame, stopping.")
        break
    cv2.imshow("Live", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

The two lines at the top set a Windows speed-up. They must come **before** `import cv2`, which is why this file breaks the usual rule that imports go first. On macOS and Linux they do no harm.

Run it from the project folder:

```bash
python exercises/day08/live_view.py
```

You should see yourself. If not, use the table above. Press `q` in the video window to stop.

Now ask a video for its properties. Create `exercises/day08/camera_info.py`. It takes a camera number or a file name on the command line:

**`exercises/day08/camera_info.py`**

```python
import sys

import cv2

source = sys.argv[1] if len(sys.argv) > 1 else "0"
source = int(source) if source.isdigit() else source  # "0" -> camera 0, "clip.mp4" stays text

cap = cv2.VideoCapture(source)
if not cap.isOpened():
    raise SystemExit(f"Cannot open {source!r}")

print("width :", int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print("height:", int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("fps   :", cap.get(cv2.CAP_PROP_FPS))
print("frames:", int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))  # a webcam has no fixed length: 0 or -1
cap.release()
```

```bash
python exercises/day08/camera_info.py          # your webcam (source 0)
python exercises/day08/camera_info.py clip.mp4 # a file
```

For a sample video file the output looks like this (your webcam will show its own size, often `1280` x `720` and `30` fps):

```text
$ python exercises/day08/camera_info.py clip.mp4
width : 810
height: 1080
fps   : 15.0
frames: 65
```

## Check yourself

1. What does `ok` mean for a webcam and for a file?
2. What is `ord("q")`?
3. Why can you not open the same webcam in two programs at once?

<details><summary>Answers</summary>

1. For a webcam: `False` means a problem, so retry. For a file: `False` means the video has ended.
2. The number that stands for the letter `q` (113). `waitKey` returns such numbers.
3. A camera gives its frames to one program. The second program is refused (or gets no frames).

</details>

---

# Hour 23: Command-line options, speed and snapshots

## Learn: `argparse`

On Day 4 you read `sys.argv` by hand. For real programs use **`argparse`**. It reads the words you type after the program name, checks them, and writes the `--help` text for you:

```python
import argparse

ap = argparse.ArgumentParser(description="Webcam security camera")
ap.add_argument("--source", help="camera index or video file (overrides config)")
ap.add_argument("--no-window", action="store_true", help="run without the preview window")
args = ap.parse_args()

args.source       # the text after --source, or None if it was not given
args.no_window    # True if --no-window was given, else False (note: "-" becomes "_")
```

- `--source clip.mp4` is an **option with a value**.
- `--no-window` with `action="store_true"` is a **flag**: present means `True`.

The source can be a camera number or a file name, but the command line always gives you **text**. So `"0"` must become the number `0` and `"clip.mp4"` must stay text. That is the job of the small function `parse_source` in the project: `int(value) if str(value).isdigit() else value`.

## Learn: speed and timestamps

**FPS** is the number of frames you handle per second. To measure it, count frames and divide by the time that passed (`time.perf_counter()` is a precise stopwatch). If your processing is slow, the FPS drops. The detector on Day 12 will make this matter.

For snapshot **file names** use the date and time, so that files never overwrite each other and sort correctly: `f"{now:%Y%m%d_%H%M%S}.jpg"` gives `20261015_195304.jpg`.

## Lab 8.2: Snapshot viewer

Create `exercises/day08/snapshot_view.py`. It shows the live picture with the time and the FPS. Press `s` to save a snapshot in the `snapshots` folder, `q` to quit.

**`exercises/day08/snapshot_view.py`**

```python
import os
import time
from datetime import datetime
from pathlib import Path

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"  # Windows: before importing cv2

import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Cannot open the camera.")

Path("snapshots").mkdir(exist_ok=True)
frames, start = 0, time.perf_counter()
fps = 0.0

print("Press s to save a snapshot, q to quit.")
while True:
    ok, frame = cap.read()
    if not ok:
        break

    frames += 1
    elapsed = time.perf_counter() - start
    if elapsed >= 1.0:  # update the speed number once per second
        fps = frames / elapsed
        frames, start = 0, time.perf_counter()

    now = datetime.now()
    cv2.putText(frame, f"{now:%Y-%m-%d %H:%M:%S}  {fps:.0f} fps", (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imshow("Snapshot view", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("s"):
        path = Path("snapshots") / f"{now:%Y%m%d_%H%M%S}.jpg"
        cv2.imwrite(str(path), frame)
        print("saved", path)
    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

Notice how FPS is updated once per second: count `frames`, and when one second has passed, divide and start counting again.

## Lab 8.3 (Milestone 4): The camera loop of the project

Now build the real program. You change three files.

**1. `intelligence/__init__.py`.** Add the Windows camera setting. `__init__.py` runs first whenever anything from the package is imported, so the setting is in place before OpenCV starts:

**`intelligence/__init__.py`**

```python
"""Security camera intelligence system: detection, tracking, memory, rules, alerts."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Windows: OpenCV's default camera backend can take 30+ seconds to open some webcams with this on.
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
```

**2. `intelligence/app.py`.** This file already has `Track` and `draw_overlay` from Days 5 and 7. Add the imports at the top, `parse_source`, and the new `main()` function at the end. Here is the complete file:

**`intelligence/app.py`**

```python
import argparse
import time
from dataclasses import dataclass, field
from datetime import datetime

import cv2

from .config import load_config
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

    source = parse_source(args.source if args.source is not None else cfg["source"])
    is_file = isinstance(source, str)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(
            f"Cannot open source {source!r}. For a camera on macOS, allow camera access for your "
            "terminal/VS Code in System Settings > Privacy & Security > Camera."
        )

    frames = 0
    print("Running. Press q in the video window, or Ctrl+C in the terminal, to quit.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                if is_file:
                    break  # the video file is finished
                print("Camera read failed, retrying...")
                time.sleep(0.5)
                continue

            frames += 1
            draw_overlay(frame, [], rules, datetime.now())

            if not args.no_window:
                cv2.imshow("Security Camera", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"Read {frames} frames.")
```

Read `main()` in order:

1. **Options:** `--source` and `--no-window`.
2. **Setup:** load the config, create the `RuleEngine` (so the overlay can draw zones), choose the source (the command line wins over `config.json`), open it. If it cannot be opened, stop with a **friendly message** (`SystemExit`, from Day 4).
3. **The loop:** read a frame. If there is no frame: a file means we are done (`break`), a webcam means wait and try again (`continue`, the retry pattern from Day 2). Otherwise draw the overlay and show it. `q` stops the loop.
4. **Cleanup:** the `finally` block always runs, even after Ctrl+C or a crash: give the camera back, close the windows, print the number of frames.

`draw_overlay(frame, [], rules, datetime.now())` passes an **empty list** of tracks, because we have no detector yet. You will see only the time (and the zone, if enabled). On Day 13 the list will fill with real tracks.

**3. `security_camera.py`.** It becomes very short: it only starts `main()`:

**`security_camera.py`**

```python
"""Security camera intelligence system. Run it from this folder:  python security_camera.py"""

from intelligence.app import main

if __name__ == "__main__":
    main()
```

**Run it.** Look at the automatic help:

```text
$ python security_camera.py --help
usage: security_camera.py [-h] [--source SOURCE] [--no-window]

Webcam security camera

options:
  -h, --help       show this help message and exit
  --source SOURCE  camera index or video file (overrides config)
  --no-window      run without the preview window
```

Run it on a video file without a window (replace `clip.mp4` with any video you have; we use a sample file here):

```text
$ python security_camera.py --source clip.mp4 --no-window
Running. Press q in the video window, or Ctrl+C in the terminal, to quit.
Read 65 frames.
```

And on your webcam, with the window. You should see yourself with the date and time at the top. Press `q` to stop:

```bash
python security_camera.py
```

**Test it.** `tests/check_app.py` checks `parse_source`, runs the whole program on a tiny video, and checks that a missing file gives a friendly error and not a traceback:

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

# Make a tiny video of 10 frames and run the whole program on it, without a window
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
assert "Read 10 frames." in result.stdout, result.stdout

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

```text
$ python -m tests.check_app
app OK
```

## Lab 8.4: Record your own test clip

From Day 12 you will test the detector on a clip of **yourself**. Create `exercises/day08/record_clip.py`. It records 15 seconds from the webcam into `clip.mp4`:

**`exercises/day08/record_clip.py`**

```python
import os
import time

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"  # Windows: before importing cv2

import cv2

SECONDS = 15

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Cannot open the camera.")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30  # some cameras report 0: then we assume 30
writer = cv2.VideoWriter("clip.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

print(f"Recording {SECONDS} seconds. Walk into the picture, stand still, then walk out.")
start = time.monotonic()
while time.monotonic() - start < SECONDS:
    ok, frame = cap.read()
    if not ok:
        break
    writer.write(frame)
    cv2.imshow("Recording (press q to stop early)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

writer.release()
cap.release()
cv2.destroyAllWindows()
print("Saved clip.mp4")
```

```bash
python exercises/day08/record_clip.py
```

During the 15 seconds: start with an **empty picture** for a few seconds, **walk in**, stand still for a moment, **walk out**, and leave the picture empty again. A clip with all of these is the best test for the whole project. Then test your loop on it:

```bash
python security_camera.py --source clip.mp4
```

Do not commit the clip: `*.mp4` is in your `.gitignore`. If you have no webcam, copy any short video (from a phone) into the project folder and call it `clip.mp4`.

## Check yourself

1. Why is `--no-window` useful?
2. What does `parse_source("0")` return? And `parse_source("clip.mp4")`?
3. What does the `finally` block guarantee in `main()`?

<details><summary>Answers</summary>

1. The program can run without a screen (a server, a test, a recorded video processed in the background) and faster.
2. `0` (a number) and `"clip.mp4"` (the text, unchanged).
3. The camera is released and the windows are closed even if the user presses Ctrl+C or the program crashes.

</details>

---

# Hour 24: Motion detection, the "before AI" method

## Learn

Before neural networks, a common way to find "something happening" was to compare frames. If a pixel's brightness changes, something may have moved there. The steps:

```text
frame ─► grey ─► blur ─► difference with a ─► threshold ─► dilate ─► contours ─► big enough? ─► box
                         reference picture    (changed?)   (join)    (blobs)
```

| Step | OpenCV | Why |
|---|---|---|
| Grey | `cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)` | colour is not needed, 1 number per pixel is faster |
| Blur | `cv2.GaussianBlur(gray, (21, 21), 0)` | smooths away tiny camera noise |
| Difference | `cv2.absdiff(reference, gray)` | `\|a - b\|` per pixel. **Safe** for `uint8` (no wrap-around, remember Day 6) |
| Threshold | `cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)` | pixels that changed by more than 25 become 255 (white), the rest 0 |
| Dilate | `cv2.dilate(mask, None, iterations=2)` | grows white areas to close small holes |
| Contours | `cv2.findContours(...)` | finds the outline of each white blob |
| Size filter | `cv2.contourArea(contour) < MIN_AREA` | ignore tiny blobs |
| Box | `cv2.boundingRect(contour)` | the `(x, y, w, h)` rectangle around a blob |

**What is the reference picture?** There are two choices and they behave very differently:

1. **Background:** compare every frame with the **first** frame (the empty scene).
2. **Previous frame:** compare every frame with the one just before it.

## Lab 8.5: Compare the two methods

First make a test video with known events, so that you know what the right answer is. `exercises/day08/make_test_clip.py` creates `motion_test.mp4`, 100 frames of a small grey room:

**`exercises/day08/make_test_clip.py`**

```python
import cv2
import numpy as np

WIDTH, HEIGHT, FPS = 320, 240, 15
writer = cv2.VideoWriter("motion_test.mp4", cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT))


def scene(brightness, square_x=None):
    """A grey room, with an optional white square (a "person") at the given x position."""
    frame = np.full((HEIGHT, WIDTH, 3), brightness, np.uint8)
    if square_x is not None:
        cv2.rectangle(frame, (square_x, 100), (square_x + 40, 140), (255, 255, 255), -1)
    return frame


for _ in range(10):  # frames 0-9:    the room is empty
    writer.write(scene(90))
for i in range(30):  # frames 10-39:  a square walks across the picture
    writer.write(scene(90, 10 + i * 8))
for _ in range(15):  # frames 40-54:  the square stands still
    writer.write(scene(90, 10 + 29 * 8))
for _ in range(15):  # frames 55-69:  the square has left, the room is empty
    writer.write(scene(90))
for _ in range(30):  # frames 70-99:  somebody switches the light on: nothing moves, but it is brighter
    writer.write(scene(150))

writer.release()
print("saved motion_test.mp4 (100 frames)")
```

```text
$ python exercises/day08/make_test_clip.py
saved motion_test.mp4 (100 frames)
```

Now the detector. Create `exercises/day08/motion_demo.py`. It uses `argparse` to choose the source and the method, and with `--timeline` it prints one character per frame (`#` = motion, `.` = quiet, `-` = the reference frame):

**`exercises/day08/motion_demo.py`**

```python
import argparse

import cv2

ap = argparse.ArgumentParser(description="A simple motion detector (frame differencing)")
ap.add_argument("--source", default="0", help="camera number or video file")
ap.add_argument("--mode", choices=["background", "previous"], default="background",
                help="compare each frame with the first frame, or with the previous frame")
ap.add_argument("--no-window", action="store_true", help="do not show a window")
ap.add_argument("--timeline", action="store_true", help="at the end, print one character per frame")
args = ap.parse_args()

source = int(args.source) if args.source.isdigit() else args.source
cap = cv2.VideoCapture(source)
if not cap.isOpened():
    raise SystemExit(f"Cannot open {source!r}")

MIN_AREA = 500  # ignore moving areas smaller than this many pixels
reference = None  # the picture we compare with
frames = moving_frames = 0
timeline = []  # one character per frame: - reference, . quiet, # motion

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frames += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)  # blur away tiny noise

    if reference is None:
        reference = gray  # the first frame is our picture of the "empty scene"
        timeline.append("-")
        continue

    difference = cv2.absdiff(reference, gray)  # safe subtraction: no uint8 wrap-around
    mask = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]  # changed pixels become 255
    mask = cv2.dilate(mask, None, iterations=2)  # fill small holes
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    moving = False
    for contour in contours:
        if cv2.contourArea(contour) < MIN_AREA:
            continue
        moving = True
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    if moving:
        moving_frames += 1
    timeline.append("#" if moving else ".")

    if args.mode == "previous":
        reference = gray  # next time compare with this frame

    if not args.no_window:
        cv2.putText(frame, "MOTION" if moving else "quiet", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if moving else (0, 200, 0), 2)
        cv2.imshow("Motion", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
print(f"{moving_frames} of {frames} frames had motion ({args.mode} mode)")
if args.timeline:
    for start in range(0, len(timeline), 50):
        print(f"{start:3d}: {''.join(timeline[start:start + 50])}")
```

Run both methods on the test video:

```text
$ python exercises/day08/motion_demo.py --source motion_test.mp4 --mode background --no-window --timeline
75 of 100 frames had motion (background mode)
  0: -.........########################################
 50: #####...............##############################
```

```text
$ python exercises/day08/motion_demo.py --source motion_test.mp4 --mode previous --no-window --timeline
32 of 100 frames had motion (previous mode)
  0: -.........##############################..........
 50: .....#..............#.............................
```

Read the two timelines against what happens in the video:

| Frames | What happens | Background method | Previous-frame method |
|---|---|---|---|
| 0-9 | empty room | quiet | quiet |
| 10-39 | the square walks | motion | motion |
| 40-54 | the square **stands still** | motion (it is not in the empty picture) | **missed** (nothing changes between frames) |
| 55-69 | the square has left | quiet | one flag at frame 55 (the moment it vanished) |
| 70-99 | **the light is switched on**, nothing moves | **motion for all 30 frames: false alarm** | one flag at frame 70, then quiet |

Both have a weakness:

- The **background** method is faithful about things that stay, but a change of light (or a moved chair, or the sun going behind a cloud) makes it shout "motion!" **forever**.
- The **previous-frame** method adapts to slow changes, but it cannot see a person who stands still.

## Lab 8.6: Try it on your camera

```bash
python exercises/day08/motion_demo.py --mode background
python exercises/day08/motion_demo.py --mode previous
```

Try each of these and write down what the detector does (a window opens; press `q` to stop):

1. Wave your hand.
2. Walk away and come back.
3. Stand still for 5 seconds.
4. Cover the camera with your hand, then uncover it.
5. If you can, switch the room light on and off.
6. Let a (paper) object swing or a curtain move.

Discuss: **what can this method *not* tell you?**

- It does not know **what** moved. A person, a cat, a shadow, a tree, a curtain and a light flicker all look the same.
- It cannot tell whether it is a person at the door or a plastic bag in the wind.
- It breaks when the light changes.

That is the problem the next days solve. On **Day 12** a neural network (YOLO) will say "this is a **person**, 91% sure" in every frame, and on **Day 13** it will follow each person with an ID. Motion detection is still useful in real systems as a cheap trigger: "something changed, wake up the expensive AI". You now know how both work.

## Check yourself (exit ticket)

1. Which method misses a person who stands still, and why?
2. Which method gives false alarms for as long as a light stays switched on?
3. Why do we blur and use a minimum area before drawing a box?
4. Name two things motion detection cannot tell you.

<details><summary>Answers</summary>

1. The previous-frame method. Nothing changes between two frames of a still person, so the difference is empty.
2. The background method. Every frame is different from the old empty picture, as long as the light is different.
3. To ignore tiny changes caused by camera noise and small flickers, so only real moving objects get a box.
4. For example: what kind of object it is (person or animal), and whether a change is real motion or only a light change.

</details>

---

# Day 8 wrap-up

## Checklist

- [ ] `live_view.py` shows your webcam (or you know why not and asked for help).
- [ ] `python security_camera.py` shows the live picture with the time; `q` quits.
- [ ] `python security_camera.py --source clip.mp4 --no-window` prints `Read N frames.`
- [ ] `python -m tests.check_app` prints `app OK`.
- [ ] You have your own `clip.mp4`.
- [ ] You ran the motion demo with both methods and can explain the difference.
- [ ] You committed (`git commit -m "Day 8: camera loop and motion demo"`).

## Your project folder today

```text
my-intelligence-system/
├── clip.mp4                    <- your recording (ignored by git)
├── security_camera.py          <- now starts main()
├── intelligence/
│   ├── __init__.py             <- Windows camera setting added
│   ├── app.py                  <- parse_source, main() added
│   └── ...
├── tests/
│   └── check_app.py            <- new
└── exercises/day08/
    ├── live_view.py
    ├── camera_info.py
    ├── snapshot_view.py
    ├── record_clip.py
    ├── make_test_clip.py
    └── motion_demo.py
```

Solutions are in [`solutions/day08/`](solutions/day08/).

## Instructor notes

- **Cameras are the biggest time sink of the whole course.** Test one student machine of each operating system *before* the lesson. Typical problems: macOS permission for Terminal vs VS Code (they are separate apps), Windows privacy switches, Zoom or Teams holding the camera, virtual cameras (OBS), a phone as camera `0`, Linux without `video` group.
- **Students without a webcam:** they use a video file named `clip.mp4`. Everything else is the same. Have two short sample videos ready on a shared drive.
- **Dark rooms and low frame rates:** cameras reduce FPS in low light. This is normal.
- **`argparse`:** let students run `--help` and read it. Then ask them to add a flag of their own (`--verbose`).
- **The `finally` block:** have one student press Ctrl+C while the window is open and look at the `Read N frames.` line, to see it still runs.
- **Motion lab:** the timeline table is the key moment of the lesson. Let students predict each row before they run the two commands. The point to take away is "motion is not understanding".
- **If you are behind:** skip Lab 8.2 (snapshots) and Lab 8.6, but never skip Lab 8.3 (the loop) or Lab 8.4 (the clip): Days 12-15 need both.
- **Fast finishers:** make `motion_demo.py` save a snapshot (with the timestamped name) the first frame of each new motion event; or show the `mask` in a second window with `cv2.imshow("mask", mask)`.

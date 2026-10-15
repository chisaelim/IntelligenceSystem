# Course Outline: Python to an AI Security Camera

**45 hours = 15 days x 3 hours.** Students start with no Python and, in the last hour, run their own
Intelligence System: a webcam that detects and tracks people, remembers what it saw, decides what
matters, and sends a photo alert to Telegram. All tools are free.

**The detailed lesson for every day** (what to teach, the code, the labs, the answers and instructor notes) is in [lessons/](lessons/README.md). This page is the overview.

**Prerequisites:** none.
**Needs:** a laptop with 8 GB RAM (the finished system uses under 1 GB), at least 15 GB free disk, a
webcam (or a video file to practise on), a Telegram account, internet.
**Environment:** Anaconda, env `python-course` (Python 3.11), VS Code and JupyterLab.

**Before Day 1 (not counted in the 45 hours):** the environment is a large download, about 3 GB on
Windows and 5 GB on Linux (more than half of it the GPU libraries that PyTorch brings) and about 4 GB
on disk on a Mac. Students should install Anaconda and create the env at home or from a shared drive,
so hour 1 only checks it. Anyone who is not ready starts the download at the beginning of hour 1 and
follows hours 1 and 2 while it runs.
The student guide for this is [lessons/00-before-day-1.md](lessons/00-before-day-1.md).

## What students build

The reference project in this repo is the finish line. Students write each module themselves, in the
order below, so every day ends with something that runs.

| Day | What they finish | Reference in this repo |
|---|---|---|
| 4 | Settings and secrets loader | `intelligence/config.py` |
| 5 | Data classes and night-time rule | `Track` (`app.py`), `Detection` (`detector.py`), `RuleEngine.is_night` (`rules.py`) |
| 7 | Drawing boxes, labels and zones on a frame | `draw_overlay` in `app.py`. The students' first version takes plain boxes and polygons; the reference takes `Track`s and the rule engine, so they upgrade it on Day 15 |
| 8 | Camera loop with `--source` / `--no-window`, plus a motion detector (the "before AI" baseline) | Camera loop and flags: `main()` in `app.py`. The motion detector is a teaching step, not part of the final system: its reference is `lessons/solutions/day08/motion_demo.py` |
| 9 | Event memory in SQLite (`hour_histogram` is added on Day 14) | `intelligence/events.py` |
| 11 | Telegram alerts from a background thread | `intelligence/telegram_bot.py` |
| 13 | YOLO detection and tracking | `intelligence/detector.py` |
| 14 | Severity rules, zones, unusual-hour check, alert-policy function | `intelligence/rules.py`. The alert policy is written inline in `main()` in the reference |
| 15 | Everything wired together and demonstrated | `app.py`, `security_camera.py` |

Each hour pairs a short talk or demo with a hands-on lab (roughly one third talk, two thirds lab).
Days 5 and 14 are the densest.

---

## Week 1: Python foundations (Days 1-5, hours 1-15)

### Day 1: Setup and first programs (hours 1-3)
| Hour | Topic | Lab |
|---|---|---|
| 1 | Anaconda tour; what a conda environment is; confirm `python-course` is installed, or create it from `environment-<os>.yml` (see "Before Day 1") | Check `import cv2, torch, ultralytics` works |
| 2 | Install VS Code; terminal basics, running a `.py` file vs a Jupyter notebook, how to read an error message | Run hello world both ways |
| 3 | Variables, numbers, strings, f-strings, `print`, `input` | Greeting program; temperature converter |

### Day 2: Decisions and functions (hours 4-6)
| Hour | Topic | Lab |
|---|---|---|
| 4 | `if`/`elif`/`else`, comparison and boolean operators | Classify a confidence score as low / medium / high |
| 5 | `for` and `while` loops, `range`, `break`/`continue` | Count frames in a loop; simple retry loop |
| 6 | Functions: parameters, return values, scope, docstrings | `assess(label, at_night, in_zone)` severity function (the heart of `rules.py`) |

### Day 3: Collections and JSON (hours 7-9)
| Hour | Topic | Lab |
|---|---|---|
| 7 | Lists, tuples, slicing, comprehensions | Filter detections by label and confidence |
| 8 | Dictionaries and sets, including set difference | Count sightings per label; unique track IDs; which zones are new for a track |
| 9 | JSON: `json.load`, nested data | Read `config.json` and print the watch list |

### Day 4: Files, errors, modules (hours 10-12)
| Hour | Topic | Lab |
|---|---|---|
| 10 | Reading and writing text files with `with open(...)`, `pathlib` paths that work on every OS | Parse a `KEY=VALUE` file |
| 11 | Exceptions (`try`/`except`), debugging with print and the VS Code debugger | Handle a missing file with a helpful message |
| 12 | Modules and packages: `import`, `__init__.py`, relative imports (`from .config import ...`), `if __name__ == "__main__"` | **Milestone 1:** put `config.py` in an `intelligence/` package and call it from `security_camera.py` |

### Day 5: Objects, time, git (hours 13-15)
| Hour | Topic | Lab |
|---|---|---|
| 13 | Classes and objects: attributes, methods, `__init__` | A `Counter` class, then a `RuleEngine` skeleton |
| 14 | `dataclass`, including `field(default_factory=set)` for list and set defaults; `datetime`, `timedelta`, `isoformat`/`strftime`, `time.monotonic` | **Milestone 2:** `Track` and `Detection`; `is_night` that works across midnight (22:00 to 06:00) |
| 15 | Git basics: init, add, commit, `.gitignore`; why secrets never go in git. **Checkpoint 1 (20 min):** Python quiz | Commit the work so far |

---

## Week 2: Images, data, networks (Days 6-10, hours 16-30)

### Day 6: NumPy (hours 16-18)
| Hour | Topic | Lab |
|---|---|---|
| 16 | Arrays, shape, dtype, indexing and slicing | Build and slice arrays |
| 17 | Vectorised math, broadcasting, why it beats loops | Time a loop vs NumPy |
| 18 | An image is a NumPy array: pixels, channels, BGR | Crop, brighten and flip an image by indexing |

### Day 7: OpenCV for images (hours 19-21)
| Hour | Topic | Lab |
|---|---|---|
| 19 | `imread`, `imshow`, `imwrite`, `waitKey`, resize, color spaces | Load, grayscale, save |
| 20 | Drawing: rectangle, text, polylines; coordinates; boxes as `x1,y1,x2,y2` | Draw labeled boxes on a photo |
| 21 | Geometry: normalised (0-1) vs pixel coordinates, polygons (a `float32` NumPy array), `pointPolygonTest` | **Milestone 3:** `draw_overlay(frame, boxes, zones)` plus "is this point inside the zone?" |

### Day 8: Video and motion (hours 22-24)
| Hour | Topic | Lab |
|---|---|---|
| 22 | `VideoCapture`: webcam vs video file, the frame loop, camera permissions on each OS | Show live webcam; quit with `q` |
| 23 | FPS, timing, saving snapshots with timestamped names; `argparse` flags `--source` (camera number or video file) and `--no-window` | Save a frame when a key is pressed; run the same script on a webcam and on a video file |
| 24 | Classic motion detection: frame differencing, blur, threshold, contours | **Milestone 4:** a webcam that boxes anything that moves. Compare two methods. Against a fixed background, a light switch causes false alarms for as long as the light stays changed. Against the previous frame it flashes only once, but a person who stands still disappears. That is why we need AI |

### Day 9: Memory with SQL (hours 25-27)
| Hour | Topic | Lab |
|---|---|---|
| 25 | Tables, rows, `INSERT`, `SELECT`, `WHERE`, `GROUP BY`, hours from a date with `strftime` | Practise queries in a SQLite viewer |
| 26 | Python `sqlite3`: connect, execute, commit, parameters (never string-build SQL) | **Milestone 5:** `EventStore.add`, `recent`, `today_summary` |
| 27 | Pretend history: generate 20 days of daytime sightings with `random`, `timedelta` and `store.add(ts=...)`; analyse with pandas and matplotlib (`read_sql`, group by hour, plot) | Chart sightings per hour. **Keep this database:** Day 14's "unusual hour" rule needs at least 30 past sightings (`anomaly.min_history`), and a classroom has far fewer, so the rule can only be shown with seeded data |

### Day 10: Talking to Telegram (hours 28-30)
| Hour | Topic | Lab |
|---|---|---|
| 28 | How the web works: HTTP, REST, status codes, JSON; the `requests` library | Call a public JSON API and read the response |
| 29 | Telegram Bot API: create a bot with BotFather, bot token, chat id, `sendMessage` | Send yourself a message from Python |
| 30 | Secrets and safety: `.env` vs environment variables (`os.environ`), never commit tokens, revoking a token; `sendPhoto` with a file upload (captions are limited to 1024 characters). **Checkpoint 2 (20 min):** NumPy / OpenCV / SQL quiz | Send a saved snapshot to your phone |

---

## Week 3: AI and the full system (Days 11-15, hours 31-45)

### Day 11: Not blocking the camera (hours 31-33)
| Hour | Topic | Lab |
|---|---|---|
| 31 | Why a slow network call freezes video; threads, `queue.Queue`, daemon threads, events | Show the freeze, then fix it with a worker thread |
| 32 | Build the notifier: queue of messages, background worker, `flush` on shutdown | **Milestone 6:** `TelegramNotifier` |
| 33 | Dry-run mode, timeouts, error handling that never prints the token | Add a `--dry-run` flag; test with it, then with the real bot |

### Day 12: Object detection with YOLO (hours 34-36)
| Hour | Topic | Lab |
|---|---|---|
| 34 | Machine learning in plain words: classification vs detection; boxes, confidence, COCO classes; non-max suppression | Predict by hand: what would a detector output? |
| 35 | PyTorch in 45 minutes: tensors, CPU vs GPU (`cuda`, `mps`), `device="auto"` | Move a tensor between devices, time it |
| 36 | Ultralytics YOLO: load `yolo11n.pt`, run on images and a video, read `results.boxes`. The first use downloads the model (5 MB, or 18 MB for `yolo11s`) | Compare `yolo11n` vs `yolo11s` for speed and accuracy; try different `conf` values |

### Day 13: Tracking (hours 37-39)
| Hour | Topic | Lab |
|---|---|---|
| 37 | Detection has no memory between frames; tracking gives each object a stable ID (ByteTrack, `persist=True`). Matching boxes between frames is an assignment problem, which is why the `lap` package is installed | Run `model.track` and print IDs over time |
| 38 | Build `Detector`: wrap YOLO, filter to the classes we watch, return `Detection` objects; handle frames with no tracked objects (`boxes.id` is `None`) | **Milestone 7:** `detector.py` |
| 39 | Track life cycle: confirm after N frames, mark as left after N seconds | Print "person #3 appeared" / "left after 12s" on live video |

### Day 14: Making it intelligent (hours 40-42)
| Hour | Topic | Lab |
|---|---|---|
| 40 | Rules as reasoning: severity score from label + night + zone; where the object touches the ground | Build `RuleEngine.assess` and `zones_for` |
| 41 | Learning from history: hourly histogram, "rare share" threshold, caching the result | Add `EventStore.hour_histogram` and the "unusual for this hour" rule; test it on the Day 9 seeded database: a person at 03:00 becomes HIGH, at noon stays medium |
| 42 | Alert policy: min severity, once per object, escalation, cooldown, written as one small function. Put the tunable values in `config.json` (the reference keeps a few constants, such as the 30-day history window, in `rules.py`: which should move?) | **Milestone 8:** `rules.py` complete plus the alert-policy function; tune with recorded clips (`--source clip.mp4`). **Checkpoint 3 (20 min):** detection / tracking / rules quiz |

### Day 15: Integration and demo (hours 43-45)
| Hour | Topic | Lab |
|---|---|---|
| 43 | Wire it together: load config and secrets, detector, rules, store, notifier, main loop, clean shutdown (`try`/`finally`); the `security_camera.py` entry point | **Milestone 9:** `app.py`: plug in the alert-policy function (inline in `main()` in the reference), add `--history` and `--config`; first full run with `--dry-run` |
| 44 | Test and tune: replay a video with `--source clip.mp4 --no-window`, fix false alerts, check `--history`; privacy and ethics of filming people; run-anywhere checks on Windows / macOS / Linux | Real Telegram alerts; each student writes a one-page tuning note |
| 45 | **Final demo: the finished Intelligence System.** Each student runs their own build live: walk into frame, receive the photo alert on their phone, show the event history | Demo, peer review, retrospective, next steps (custom models, face blur, cloud storage) |

---

## Assessment

| Item | Weight | When |
|---|---|---|
| Daily lab handed in (files for Days 1-4, git commits from Day 5) | 30% | Days 1-14 |
| Checkpoints 1, 2, 3 (20 minutes each) | 30% | Hours 15, 30, 42 |
| Final project demo (works, alert received, code explained) | 40% | Hour 45 |

**Final project rubric:** detects and tracks people (20) · stores events in SQLite (15) · severity rules
with at least night, zone and one rule of the student's own (25) · Telegram photo alert, token kept out
of git (20) · clean code and a short README (10) · explains one false alarm and how they reduced it (10).

## Packages and concepts covered

| Area | Items |
|---|---|
| Python | variables, control flow, functions, collections, files, exceptions, modules and relative imports, `argparse`, classes, `dataclass`, `datetime`, `pathlib`, `json`, `random`, `os.environ`, `threading`, `queue`, `sqlite3` |
| Data and images | NumPy, pandas, matplotlib, OpenCV |
| Web | HTTP and REST, `requests`, Telegram Bot API |
| AI | detection vs classification, confidence and NMS, YOLO11 (ultralytics), PyTorch tensors and devices, ByteTrack tracking |
| Engineering | conda environments, git and `.gitignore`, secrets handling, config files, dry-run testing, debugging, privacy and ethics |

The `python-course` environment also holds TensorFlow, scikit-learn, scikit-image and SciPy. This course
does not use them.

## Instructor notes

- **Buffer:** if a day runs over, the charting half of hour 27 and hour 35 (PyTorch tensors) can be
  shortened. Keep the history seeding in hour 27, because Day 14 needs it. Do not cut Day 8, 11 or 13: the
  final project depends on them.
- **Before Day 1:** see the install note at the top. Also have every student check webcam permission and
  create a Telegram account; Windows students may need to accept conda terms of service once.
- **Before Day 10:** each student creates a bot with BotFather and sends it one message, so the chat id
  can be read.
- **Safety net:** `lessons/solutions/dayNN` holds the files students write on each day: the exercise files
  directly in the folder and the project files in `dayNN/project/`. A student who falls behind gets the missing
  day's files with `python lessons/solutions/assemble.py --only N <project folder>` (see
  `lessons/solutions/README.md`). Do not hand out the solutions in advance.
- **Demo day (hour 45):** a second alert within `alert.cooldown_seconds` (default 30) of the last one is
  suppressed unless it is HIGH, so students testing one after another should lower it to about 5 in their
  config. To show the "unusual for this hour" rule, point a second config file (`--config`) at the seeded
  database from Day 9, so fake history never mixes with real sightings.
- **Speed:** measured on an Apple-silicon Mac with a test photo, the detector runs at about 25 frames
  per second on the CPU alone and about 90 with the GPU. Older CPU-only laptops will be slower (not
  measured); lowering `image_size` to 480 in `config.json` helps if the preview lags.
- **Licence:** YOLO11 (ultralytics) is AGPL-3.0. It is free for learning and for open-source projects;
  a closed or commercial product needs an Ultralytics enterprise licence. Mention this before students
  take the project further.
- **Ethics:** the camera should only record places and people the student has permission to record.

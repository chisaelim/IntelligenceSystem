# Lessons: from first Python line to an AI security camera

Fifteen days, three hours per day, 45 hours in all. Day by day, students build their own copy of the Intelligence System that is in this repository. In the last hour they show it working: a webcam that detects and follows people, remembers what it saw, decides what matters, and sends a photo alert to Telegram.

This folder holds **one detailed lesson per day**, a guide for the setup before Day 1, and the **solution code for every day**. The overview of the whole course (hours, topics, assessment) is in [../COURSE_OUTLINE.md](../COURSE_OUTLINE.md).

## The lessons

| Day | Hours | Lesson | What students build |
|---|---|---|---|
| 0 | before class | [Get your computer ready](00-before-day-1.md) | Anaconda, the `python-course` environment, VS Code, Git, Telegram |
| 1 | 1-3 | [Setup and first programs](day-01-setup-and-first-programs.md) | environment check, variables, `input`, f-strings |
| 2 | 4-6 | [Decisions and functions](day-02-decisions-and-functions.md) | `if`, loops, the first severity function |
| 3 | 7-9 | [Lists, dictionaries, sets and JSON](day-03-collections-and-json.md) | severity rules that read `config.json` |
| 4 | 10-12 | [Files, errors and modules](day-04-files-errors-and-modules.md) | **Milestone 1:** `intelligence/config.py`, `.env` |
| 5 | 13-15 | [Objects, time and git](day-05-objects-time-and-git.md) | **Milestone 2:** `Detection`, `Track`, `is_night`; **Checkpoint 1** |
| 6 | 16-18 | [NumPy and images as arrays](day-06-numpy.md) | arrays, crop, brightness, zone corners in pixels |
| 7 | 19-21 | [OpenCV for images](day-07-opencv-images.md) | **Milestone 3:** `draw_overlay`, `zone_polygons` |
| 8 | 22-24 | [Video and motion](day-08-video-and-motion.md) | **Milestone 4:** the camera loop, your own clip, motion detector |
| 9 | 25-27 | [Memory with SQL](day-09-sql-and-memory.md) | **Milestone 5:** `EventStore`, pretend history, chart |
| 10 | 28-30 | [Talking to Telegram](day-10-http-and-telegram.md) | your bot, a photo on your phone; **Checkpoint 2** |
| 11 | 31-33 | [Not blocking the camera](day-11-threads-and-notifier.md) | **Milestone 6:** `TelegramNotifier` (worker thread) |
| 12 | 34-36 | [Object detection with YOLO](day-12-object-detection-with-yolo.md) | IoU and NMS, PyTorch, YOLO on pictures and video |
| 13 | 37-39 | [Tracking](day-13-tracking.md) | **Milestone 7:** `Detector`, appeared / left |
| 14 | 40-42 | [Making it intelligent](day-14-rules-and-alert-policy.md) | **Milestone 8:** `RuleEngine`, history rule, alert policy; **Checkpoint 3** |
| 15 | 43-45 | [Integration and the final demo](day-15-integration-and-demo.md) | **Milestone 9:** the finished system, final demo in hour 45 |

## How a lesson is built

Every lesson has the same parts, so you always know where you are:

1. **What you can do at the end of today**, and **where today fits in the project**.
2. **A plan for the day** with minutes for each activity (each hour is about 15 minutes of talk and demo and 45 minutes of lab).
3. For each hour: **Learn** (the idea), live-demo examples, **Labs** with the code, and **Check yourself** questions with answers.
4. A **wrap-up** with a checklist, the project folder as it should look, and **instructor notes** (common mistakes, how to adapt if you are behind, ideas for fast finishers).

Conventions:

- Code blocks with a **file name above them** are files to create or change in the student's project. Blocks called `(part)`, "add inside class ..." and so on show only the new lines and where to put them.
- Blocks that begin with `$ python ...` show the **real output** of that command. `>>>` blocks are the Python console.
- Always run commands from the **project folder** (`my-intelligence-system`), with the `python-course` environment active.
- The self-checks are run with `python -m tests.check_xxx` (and from Day 15 with `python -m tests.check_all`).

## What students build, and where

Each student works in their own folder, `my-intelligence-system`. It grows like this:

```text
my-intelligence-system/
├── .env  .env.example  .gitignore  README.md      (secrets, ignore list, README)
├── config.json  config.demo.json                  (settings)
├── security_camera.py                             (the program you start)
├── intelligence/                                  (the package: config, rules, detector, events, telegram_bot, app)
├── tools/                                         (SQL helper, Telegram checks, history, chart, explain_rules)
├── tests/                                         (small self-checks, check_all runs them all)
└── exercises/day01 ... day13/                     (practice files of each day)
```

The reference project in the root of this repository is the finished answer. A student's final project must behave the same way as it: the final solution here was compared with it, row by row, on the same video.

## The solutions

[`solutions/`](solutions/README.md) has one folder per day, `day01` ... `day15`. A day's folder holds the files students write on that day: the **exercise files directly in the folder** (`day04/parse_env.py`) and the **project files in `dayNN/project/`** (`day04/project/intelligence/config.py`), where a project file has the path it has in a student's project. A project file such as `app.py` is written in stages, and a later day replaces the same file from an earlier day. So the project at the end of day N is the `project/` folders of `day01` to `dayN` copied over each other, in order.

The script [`solutions/assemble.py`](solutions/assemble.py) does it for you, with the same command on every system:

```bash
python lessons/solutions/assemble.py 8 my-intelligence-system           # the project as it is at the end of day 8
python lessons/solutions/assemble.py --only 8 my-intelligence-system    # only day 8's files, for a student who fell behind
```

**Keep the solutions and the reference project away from students until they need them.** If they have the answers from the beginning, many will copy instead of think.

## Before you teach

| When | Prepare |
|---|---|
| Two weeks before | Send students [Get your computer ready](00-before-day-1.md). The environment is a 3 to 5 GB download. |
| One week before | Test the whole project on one computer of each operating system you will teach on (Windows, macOS, Linux) with the demo settings of Day 15. Test Telegram on the classroom network. |
| Day 8 | Test one webcam on each system. Camera permissions cost more time than any other topic. Have a sample video for students without a webcam. |
| Day 10 | Every student needs a Telegram account. |
| Day 12 | The YOLO model files (5.6 MB and 19 MB) are downloaded from GitHub. For a big class, put them on a shared drive (`models/`). |
| Day 15 | A phone hotspot as a backup for the Wi-Fi. Decide how you will run the demos (5 minutes each, or stations if the class is big). |

Teaching habits that work with this material:

- **Live-code, and make students type.** Predict first ("what will it print?"), then run.
- **Pair students** for the labs, and rotate every day.
- **Commit every day** (Day 5 onward) so that students always have a working version to return to.
- Use the **exit tickets**, and the three **checkpoint quizzes** (hours 15, 30 and 42), to find out who needs help before the next step.
- When something breaks, **read the error together**. Teaching that is more valuable than the topic of the day.

## What was verified, and what was not

Every code block and every console output in the lessons comes from running the solution code. On the author's computer (a Mac with an Apple chip, Python 3.11, NumPy 2.1, OpenCV 4.12, PyTorch 2.10, ultralytics 8.4) all of these pass:

- every self-check, including the end-to-end test on a video (`python -m tests.check_all`: 10 checks);
- the final project on a video, compared row by row with the reference project in the root of the repository (identical database rows).

**Not tested:**

- Windows and Linux. The environment files were checked with a simulated install (they resolve), and the code uses only cross-platform tools, but the lessons were not run on those systems.
- A real webcam and a real Telegram bot. The code that uses them was tested with videos, with a fake network and with a fake token (Telegram answers `401`). Your first real run of Days 8, 10 and 15 is the real test.
- Teaching time. The minutes in each plan are estimates; Days 5 and 14 are the densest.

Numbers that depend on the computer (times, speeds, the device `mps`/`cuda`/`cpu`, version numbers, confidences that can differ by about 0.01) will be different on other computers. The lessons say so where it matters.

## Licence note for YOLO

The `ultralytics` package and the YOLO11 models are published under the **AGPL-3.0** licence. It is free for learning and for open-source projects. A closed or commercial product needs a different (paid) licence from Ultralytics. Tell students before they take the project further.

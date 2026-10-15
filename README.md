# Security Camera Intelligence System

A webcam security camera that detects people, vehicles and pets with YOLO, remembers what it has
seen in a local SQLite database, decides how serious each sighting is, and sends a photo alert to a
Telegram bot. Everything is free and runs locally; only the Telegram alert uses the internet.

Works on Windows, macOS and Linux with the `python-course` conda environment.

## How it works

```
webcam -> YOLO11 + ByteTrack -> rules (night? zone? unusual hour?) -> SQLite memory -> Telegram photo
          detector.py           rules.py                              events.py       telegram_bot.py
```

| File | Job |
|---|---|
| `security_camera.py` | Entry point |
| `intelligence/app.py` | Main loop: ties the pieces together, draws the preview window |
| `intelligence/detector.py` | YOLO detection + tracking, so each object keeps one ID |
| `intelligence/rules.py` | Severity score (see below) |
| `intelligence/events.py` | SQLite event log, the system's memory |
| `intelligence/telegram_bot.py` | Sends alerts from a background thread so video never stalls |
| `intelligence/config.py` | Reads `config.json` and `.env` |
| `config.json` | All settings: classes to watch, severity, night hours, zones, cooldown |
| `.env` | Your Telegram token and chat id (you create it, it is git-ignored) |
| `environment-*.yml` | Package lists for the `python-course` env (one per operating system) |

### How an alert is decided

Each object must be tracked for `min_track_frames` frames before it counts, which filters out flicker.
Then it gets a severity from 0 to 3:

| Part of the score | Points |
|---|---|
| Base value of the label (`label_severity` in `config.json`) | 0 to 3 (0 = logged, never alerted) |
| It is night (`night_hours`) | +1 |
| It is inside an enabled zone | +1 |
| It is rare for this hour, based on the last 30 days of history | +1 |

A photo alert is sent when the severity reaches `alert.min_severity` (default 2, "medium"), once per
object, and again only if it becomes more serious. `alert.cooldown_seconds` limits how often alerts are
sent; severity 3 ("HIGH") ignores the cooldown.

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) in Telegram and copy the token.
2. Send any message to your new bot, then open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy the number in `"chat":{"id": ...}`.
3. Copy `.env.example` to `.env` and fill in the token and chat id.
4. Add the packages to the `python-course` env with the file for your system
   (Windows: use **Anaconda Prompt**), run from this folder:
   ```
   conda env update -f environment-macos.yml --prune      # macOS
   conda env update -f environment-windows.yml --prune    # Windows
   conda env update -f environment-linux.yml --prune      # Linux
   ```
   If the env does not exist yet, use `conda env create -f <file>` instead.

Never commit or share `.env`. If the token leaks, revoke it with `/revoke` in @BotFather.

## Run

```
conda activate python-course
python security_camera.py                 # live camera, alerts go to Telegram
python security_camera.py --dry-run       # print alerts instead of sending (no Telegram needed)
python security_camera.py --source clip.mp4 --no-window
python security_camera.py --history 20    # what has the system seen?
```

Press `q` in the preview window (or Ctrl+C) to quit. The first run downloads `yolo11n.pt` (~6 MB)
into `models/`. Events are stored in `data/events.db` and alert photos in `snapshots/`.

## Platform notes

- **macOS:** allow camera access for Terminal / VS Code in System Settings > Privacy & Security > Camera.
  On Apple Silicon the GPU (`mps`) is used. The warning `torchvision::nms is not currently supported on
  the MPS backend` is harmless: one small step runs on the CPU. Set `"device": "cpu"` to avoid it.
- **Windows:** allow camera access in Settings > Privacy > Camera. If a conda command asks you to accept
  terms of service, run the `conda tos accept ...` command it prints.
- **Linux:** the webcam is `/dev/video0` and your user must be in the `video` group. On a machine with no
  screen, add `--no-window`.
- With an NVIDIA GPU, `"device": "auto"` uses it on Windows and Linux; otherwise the CPU is used.

## Troubleshooting

| Problem | Try |
|---|---|
| `Cannot open source 0` | Another app is using the camera, camera permission is off, or try `--source 1` |
| `Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID` | Create `.env` from `.env.example`, or use `--dry-run` |
| `[telegram] sendMessage failed: 400/403` | You have not sent your bot a message yet, or the chat id is wrong |
| Too many false alerts | Raise `confidence` or `min_track_frames`, or lower `label_severity` for that label |
| Too slow | Close other apps, lower `image_size` (e.g. 480), or keep the `yolo11n.pt` model |

## Privacy

The camera saves photos of people to `snapshots/` and sends them to your Telegram chat. Only point it
at places where you have permission to record, and tell people who may be filmed.

## Things for students to try

- Change `watch_classes` or `label_severity` in `config.json`.
- Set `"enabled": true` on the `front_door` zone and move its polygon (values are 0-1 fractions of the frame).
- Change `night_hours` and watch the severity of a person rise.
- Swap `model` to `yolo11s.pt` and compare speed and accuracy.
- Read `data/events.db` with the `sqlite3` module or `pandas.read_sql` and plot sightings per hour.

## Teaching with this project

[COURSE_OUTLINE.md](COURSE_OUTLINE.md) is a 45-hour course (15 days of 3 hours) that ends with students building their own copy of
this system. The detailed lessons, with code, labs, answers and the solution for every day, are in [lessons/](lessons/README.md).

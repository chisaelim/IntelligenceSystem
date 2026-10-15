# My Intelligence System

*One sentence: what does your system do, and where would you use it?*

## How it works

*Draw or describe the pipeline in your own words: camera, detector, tracker, rules, memory, alert.
Which file does each step?*

## How to run it

```bash
conda activate python-course
python security_camera.py --dry-run      # test without sending anything
python security_camera.py                # real alerts to Telegram
python security_camera.py --history 20   # what has it seen?
python -m tests.check_all                # all self-checks
```

Setup: copy `.env.example` to `.env` and fill in your Telegram token and chat id (never commit `.env`).

## My settings

| Setting (`config.json`) | My value | Why |
|---|---|---|
| `confidence` | | |
| `min_track_frames` | | |
| `lost_seconds` | | |
| `alert.cooldown_seconds` | | |

## My own rule

*Which rule did you add to `RuleEngine.assess`? Why does it make sense? Where is its test?*

## One false alarm (or miss) and how I reduced it

*Copy your tuning note here or link to it.*

## What I learned

*Three things. What was the hardest part?*

## Privacy

*Where does the camera look? Who knows about it? Where are the photos kept, and when do you delete them?*

"""
Security camera intelligence system.

Run (inside the python-course conda env, from this folder):
    python security_camera.py                  # live camera, alerts to Telegram
    python security_camera.py --dry-run        # print alerts instead of sending them
    python security_camera.py --source clip.mp4 --no-window
    python security_camera.py --history 20     # what has the system seen?

Telegram token and chat id come from .env, everything else from config.json.
Press "q" in the preview window (or Ctrl+C) to quit.
"""

from intelligence.app import main

if __name__ == "__main__":
    main()

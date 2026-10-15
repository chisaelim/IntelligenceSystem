import json
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
from ultralytics.utils import ASSETS

from intelligence.config import load_config
from intelligence.events import EventStore

with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)

    # A short video made from one photo: 12 identical frames
    frame = cv2.imread(str(ASSETS / "bus.jpg"))
    height, width = frame.shape[:2]
    video = folder / "bus_clip.mp4"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"mp4v"), 10, (width, height))
    for _ in range(12):
        writer.write(frame)
    writer.release()

    # A private copy of the settings: the test must not touch your real history or snapshots
    cfg = load_config()
    cfg["paths"]["database"] = str(folder / "events.db")
    cfg["paths"]["snapshots"] = str(folder / "snapshots")
    config_file = folder / "config.json"
    config_file.write_text(json.dumps(cfg))

    command = [sys.executable, "security_camera.py", "--config", str(config_file)]
    result = subprocess.run(command + ["--source", str(video), "--no-window", "--dry-run"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    out = result.stdout

    # 1. The track life cycle: everything that appeared also left
    appeared = [line for line in out.splitlines() if " appeared" in line]
    left = [line for line in out.splitlines() if " left after" in line]
    assert any("bus" in line for line in appeared), out
    assert sum("person" in line for line in appeared) >= 3, out
    assert len(left) == len(appeared), "every object that appeared must also be reported as left"

    # 2. Alerts: a snapshot was saved and the alert was "sent" (dry run, so only printed)
    assert "[telegram dry-run] sendMessage: Security camera started" in out
    assert "[telegram dry-run] sendPhoto" in out, out
    assert "[telegram dry-run] sendMessage: Security camera stopped" in out
    assert list((folder / "snapshots").glob("*.jpg")), "no snapshot was saved"

    # 3. Memory: the events are in the database
    store = EventStore(folder / "events.db")
    kinds = {row[1] for row in store.recent(100)}
    assert {"appeared", "alert", "left"} <= kinds, kinds
    persons = [row for row in store.today_summary() if row[0] == "person"]
    assert persons and persons[0][1] >= 3 and persons[0][2] >= 1, store.today_summary()
    store.close()

    # 4. --history prints what the system has seen
    history = subprocess.run(command + ["--history", "5"], capture_output=True, text=True)
    assert history.returncode == 0, history.stderr
    assert "Today's summary" in history.stdout and "Last 5 events" in history.stdout, history.stdout
    assert "person" in history.stdout

print(f"pipeline OK: {len(appeared)} objects appeared and left, alerts sent, events saved")

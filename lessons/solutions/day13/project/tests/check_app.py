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

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

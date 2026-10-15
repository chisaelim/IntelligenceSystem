from datetime import datetime
from pathlib import Path

import cv2
from ultralytics.utils import ASSETS

from intelligence.app import Track, draw_overlay
from intelligence.config import load_config
from intelligence.rules import RuleEngine

cfg = load_config()
cfg["zones"][0]["enabled"] = True  # switch the front_door zone on for this test
rules = RuleEngine(cfg)

# zone_polygons: one zone, four corners, in pixels
polygons = rules.zone_polygons((1080, 810, 3))
assert len(polygons) == 1 and polygons[0][0] == "front_door"
assert polygons[0][1].shape == (4, 2)

frame = cv2.imread(str(ASSETS / "bus.jpg"))
original = frame.copy()

tracks = [
    Track(1, "person", 0.0, 0.0, box=(47, 400, 239, 904), confirmed=True, severity=3, zones={"front_door"}),
    Track(2, "person", 0.0, 0.0, box=(671, 395, 810, 879), confirmed=True, severity=2),
    Track(3, "bus", 0.0, 0.0, box=(4, 229, 796, 728), confirmed=False),
]
draw_overlay(frame, tracks, rules, datetime(2026, 3, 14, 23, 30, 15))

assert (frame != original).any(), "draw_overlay did not change the picture"
assert tuple(frame[400, 100]) == (0, 0, 255), "severity 3 box should be red"
assert tuple(frame[395, 700]) == (0, 165, 255), "severity 2 box should be orange"
assert tuple(frame[229, 400]) == (120, 120, 120), "an unconfirmed track should be grey"

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/day07_overlay.jpg", frame)
print("overlay OK, saved output/day07_overlay.jpg")

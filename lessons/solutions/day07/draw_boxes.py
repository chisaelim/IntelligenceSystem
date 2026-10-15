from pathlib import Path

import cv2
from ultralytics.utils import ASSETS

image = cv2.imread(str(ASSETS / "bus.jpg"))

# (label, confidence, (x1, y1, x2, y2)) from a detector run. You will get these yourself on Day 12.
detections = [
    ("bus", 0.94, (4, 229, 796, 728)),
    ("person", 0.89, (671, 395, 810, 879)),
    ("person", 0.88, (47, 400, 239, 904)),
    ("person", 0.86, (223, 409, 344, 860)),
    ("person", 0.62, (0, 556, 69, 872)),
]

GREEN, ORANGE = (0, 200, 0), (0, 165, 255)  # colours are (blue, green, red)

for label, confidence, (x1, y1, x2, y2) in detections:
    color = ORANGE if label == "person" else GREEN
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
    text = f"{label} {confidence:.2f}"
    cv2.putText(image, text, (x1, max(y1 - 8, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/day07_boxes.jpg", image)
print("saved output/day07_boxes.jpg")

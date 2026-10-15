from pathlib import Path

import cv2
from ultralytics.utils import ASSETS

image = cv2.imread(str(ASSETS / "bus.jpg"))
height, width = image.shape[:2]

small = cv2.resize(image, (width // 2, height // 2))  # note: (width, height) order!
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
print("original:", image.shape)
print("small   :", small.shape)
print("gray    :", gray.shape)

Path("output").mkdir(exist_ok=True)
ok = cv2.imwrite("output/day07_small.jpg", small)
print("saved small picture:", ok)
cv2.imwrite("output/day07_gray.jpg", gray)

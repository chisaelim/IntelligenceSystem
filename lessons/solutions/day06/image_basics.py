from pathlib import Path

import cv2
from ultralytics.utils import ASSETS

image = cv2.imread(str(ASSETS / "bus.jpg"))
print("shape:", image.shape)  # (height, width, channels)
print("data type:", image.dtype)
height, width, channels = image.shape
print(f"{width} x {height} pixels, {channels} colour channels")
print("pixel at row 300, column 400 (B, G, R):", image[300, 400])

# Crop one person with a box (x1, y1, x2, y2) in pixels. Rows come first: image[y1:y2, x1:x2]
x1, y1, x2, y2 = 47, 400, 239, 904
person = image[y1:y2, x1:x2]
print("crop shape:", person.shape)

mirror = image[:, ::-1]  # every row, columns in reverse order
rgb = image[..., ::-1]  # reverse the colour channels: BGR -> RGB
print("mirror shape:", mirror.shape)
print("same pixel as (R, G, B):", rgb[300, 400])

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/day06_person.jpg", person)
cv2.imwrite("output/day06_mirror.jpg", mirror)

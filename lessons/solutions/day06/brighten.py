from pathlib import Path

import cv2
import numpy as np
from ultralytics.utils import ASSETS

image = cv2.imread(str(ASSETS / "bus.jpg"))

wrong = image + 60  # uint8 wraps around: 235 + 60 becomes 39
right = np.clip(image.astype(np.int16) + 60, 0, 255).astype(np.uint8)

print("original pixel :", image[300, 400])
print("wrong (wrapped):", wrong[300, 400])
print("right (clipped):", right[300, 400])

# Put the three pictures side by side (shrink them first so the result is small)
small = [cv2.resize(p, (270, 360)) for p in (image, wrong, right)]
summary = np.hstack(small)

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/day06_summary.jpg", summary)
print("saved output/day06_summary.jpg", summary.shape)

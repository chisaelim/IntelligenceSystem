import json

import numpy as np

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

width, height = 810, 1080  # the size of bus.jpg
zone = cfg["zones"][0]

# The corners in config.json are fractions from 0 to 1. Multiply by the picture size.
polygon = np.array(zone["polygon"], dtype=np.float32) * np.array([width, height], dtype=np.float32)

print(zone["name"], "corners in pixels:")
print(polygon)
print("as whole numbers, ready to draw:")
print(polygon.astype("int32"))

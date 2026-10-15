import cv2
import numpy as np

# A zone as a polygon in pixels: a rectangle from (100, 100) to (400, 300)
zone = np.array([[100, 100], [400, 100], [400, 300], [100, 300]], dtype=np.float32)

points = {"inside": (250, 200), "outside": (50, 50), "on the edge": (100, 200)}
for name, point in points.items():
    result = cv2.pointPolygonTest(zone, point, False)
    print(f"{name:12} {point} -> {result}")

# Where does a person "stand"? At the bottom centre of the box, where the feet touch the ground.
box = (150, 120, 250, 280)  # x1, y1, x2, y2
foot = ((box[0] + box[2]) / 2, box[3])
print("feet at", foot, "->", cv2.pointPolygonTest(zone, foot, False))

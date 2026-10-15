import sys

import cv2

source = sys.argv[1] if len(sys.argv) > 1 else "0"
source = int(source) if source.isdigit() else source  # "0" -> camera 0, "clip.mp4" stays text

cap = cv2.VideoCapture(source)
if not cap.isOpened():
    raise SystemExit(f"Cannot open {source!r}")

print("width :", int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print("height:", int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print("fps   :", cap.get(cv2.CAP_PROP_FPS))
print("frames:", int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))  # a webcam has no fixed length: 0 or -1
cap.release()

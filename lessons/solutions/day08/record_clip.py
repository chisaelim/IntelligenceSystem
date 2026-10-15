import os
import time

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"  # Windows: before importing cv2

import cv2

SECONDS = 15

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Cannot open the camera.")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30  # some cameras report 0: then we assume 30
writer = cv2.VideoWriter("clip.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

print(f"Recording {SECONDS} seconds. Walk into the picture, stand still, then walk out.")
start = time.monotonic()
while time.monotonic() - start < SECONDS:
    ok, frame = cap.read()
    if not ok:
        break
    writer.write(frame)
    cv2.imshow("Recording (press q to stop early)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

writer.release()
cap.release()
cv2.destroyAllWindows()
print("Saved clip.mp4")

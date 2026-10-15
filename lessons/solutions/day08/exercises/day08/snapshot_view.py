import os
import time
from datetime import datetime
from pathlib import Path

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"  # Windows: before importing cv2

import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise SystemExit("Cannot open the camera.")

Path("snapshots").mkdir(exist_ok=True)
frames, start = 0, time.perf_counter()
fps = 0.0

print("Press s to save a snapshot, q to quit.")
while True:
    ok, frame = cap.read()
    if not ok:
        break

    frames += 1
    elapsed = time.perf_counter() - start
    if elapsed >= 1.0:  # update the speed number once per second
        fps = frames / elapsed
        frames, start = 0, time.perf_counter()

    now = datetime.now()
    cv2.putText(frame, f"{now:%Y-%m-%d %H:%M:%S}  {fps:.0f} fps", (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imshow("Snapshot view", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("s"):
        path = Path("snapshots") / f"{now:%Y%m%d_%H%M%S}.jpg"
        cv2.imwrite(str(path), frame)
        print("saved", path)
    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

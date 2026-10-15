import os

# Windows: faster webcam start. This must be set BEFORE cv2 is imported.
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

import cv2

cap = cv2.VideoCapture(0)  # 0 = the first camera
if not cap.isOpened():
    raise SystemExit("Cannot open the camera. Check the camera permission and the camera number.")

print("Press q in the video window to quit.")
while True:
    ok, frame = cap.read()
    if not ok:
        print("No frame, stopping.")
        break
    cv2.imshow("Live", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

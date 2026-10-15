import argparse

import cv2

ap = argparse.ArgumentParser(description="A simple motion detector (frame differencing)")
ap.add_argument("--source", default="0", help="camera number or video file")
ap.add_argument("--mode", choices=["background", "previous"], default="background",
                help="compare each frame with the first frame, or with the previous frame")
ap.add_argument("--no-window", action="store_true", help="do not show a window")
ap.add_argument("--timeline", action="store_true", help="at the end, print one character per frame")
args = ap.parse_args()

source = int(args.source) if args.source.isdigit() else args.source
cap = cv2.VideoCapture(source)
if not cap.isOpened():
    raise SystemExit(f"Cannot open {source!r}")

MIN_AREA = 500  # ignore moving areas smaller than this many pixels
reference = None  # the picture we compare with
frames = moving_frames = 0
timeline = []  # one character per frame: - reference, . quiet, # motion

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frames += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)  # blur away tiny noise

    if reference is None:
        reference = gray  # the first frame is our picture of the "empty scene"
        timeline.append("-")
        continue

    difference = cv2.absdiff(reference, gray)  # safe subtraction: no uint8 wrap-around
    mask = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]  # changed pixels become 255
    mask = cv2.dilate(mask, None, iterations=2)  # fill small holes
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    moving = False
    for contour in contours:
        if cv2.contourArea(contour) < MIN_AREA:
            continue
        moving = True
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    if moving:
        moving_frames += 1
    timeline.append("#" if moving else ".")

    if args.mode == "previous":
        reference = gray  # next time compare with this frame

    if not args.no_window:
        cv2.putText(frame, "MOTION" if moving else "quiet", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if moving else (0, 200, 0), 2)
        cv2.imshow("Motion", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
print(f"{moving_frames} of {frames} frames had motion ({args.mode} mode)")
if args.timeline:
    for start in range(0, len(timeline), 50):
        print(f"{start:3d}: {''.join(timeline[start:start + 50])}")

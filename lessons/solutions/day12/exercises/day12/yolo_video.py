import sys

from ultralytics import YOLO

source = sys.argv[1] if len(sys.argv) > 1 else "clip.mp4"
model = YOLO("models/yolo11n.pt")

frames = 0
# stream=True gives the results one frame at a time instead of keeping the whole video in memory
for result in model(source, stream=True, conf=0.5, verbose=False):
    labels = sorted(model.names[int(c)] for c in result.boxes.cls.tolist())
    if frames % 15 == 0:  # print one frame in every 15
        print(f"frame {frames:3d}: {labels}")
    frames += 1

print("processed", frames, "frames")

import sys

from ultralytics import YOLO

source = sys.argv[1] if len(sys.argv) > 1 else "clip.mp4"
model = YOLO("models/yolo11n.pt")

all_ids = set()
results = model.track(source, stream=True, persist=True, tracker="bytetrack.yaml",
                      conf=0.45, classes=[0], verbose=False)  # classes=[0]: persons only
for frame_number, result in enumerate(results):
    # When nothing is being tracked, result.boxes.id is None (not an empty list!)
    ids = [] if result.boxes.id is None else result.boxes.id.int().tolist()
    all_ids.update(ids)
    if frame_number % 10 == 0:
        print(f"frame {frame_number:3d}: track ids {ids}")

print("different persons seen:", len(all_ids), sorted(all_ids))

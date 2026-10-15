from ultralytics import YOLO
from ultralytics.utils import ASSETS

model = YOLO("models/yolo11n.pt")

print("confidence threshold -> number of objects found")
for name in ("bus.jpg", "zidane.jpg"):
    print(f"\n{name}")
    for conf in (0.10, 0.25, 0.50, 0.75, 0.90):
        result = model(str(ASSETS / name), conf=conf, verbose=False)[0]
        labels = sorted(model.names[int(c)] for c in result.boxes.cls.tolist())
        print(f"  conf >= {conf:.2f}: {len(labels):2d}  {labels}")

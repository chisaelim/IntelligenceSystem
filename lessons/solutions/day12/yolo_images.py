from pathlib import Path

import cv2
from ultralytics import SETTINGS, YOLO
from ultralytics.utils import ASSETS

SETTINGS.update(sync=False)  # no anonymous usage statistics (saved once in a settings file)

Path("models").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)

model = YOLO("models/yolo11n.pt")  # downloaded the first time (about 5 MB)
print("The model knows", len(model.names), "kinds of objects. The first five:", [model.names[i] for i in range(5)])

for name in ("bus.jpg", "zidane.jpg"):
    result = model(str(ASSETS / name), conf=0.5, verbose=False)[0]
    print(f"\n{name}: {len(result.boxes)} objects")
    for box, cls, conf in zip(result.boxes.xyxy.tolist(), result.boxes.cls.tolist(), result.boxes.conf.tolist()):
        x1, y1, x2, y2 = (round(v) for v in box)
        print(f"  {model.names[int(cls)]:7} {conf:.2f}  box=({x1}, {y1}, {x2}, {y2})")

    cv2.imwrite(f"output/day12_{Path(name).stem}.jpg", result.plot())  # YOLO draws the boxes for us

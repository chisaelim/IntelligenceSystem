from dataclasses import dataclass

import torch
from ultralytics import SETTINGS, YOLO

# No anonymous usage analytics from ultralytics.
try:
    SETTINGS.update(sync=False)
except Exception:
    pass


@dataclass
class Detection:
    track_id: int
    label: str
    confidence: float
    box: tuple  # x1, y1, x2, y2 in pixels


def pick_device(preference="auto"):
    if preference != "auto":
        return preference
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class Detector:
    """YOLO object detection with ByteTrack so each object keeps a stable ID."""

    def __init__(self, model_path, watch_classes, confidence, image_size, device="auto"):
        self.model = YOLO(str(model_path))
        self.device = pick_device(device)
        self.confidence = confidence
        self.image_size = image_size

        names = self.model.names  # {class_id: name}
        unknown = [c for c in watch_classes if c not in names.values()]
        if unknown:
            raise ValueError(f"Unknown class names in watch_classes: {unknown}")
        self.class_ids = [i for i, n in names.items() if n in watch_classes]

    def track(self, frame):
        result = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=self.class_ids,
            conf=self.confidence,
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )[0]
        boxes = result.boxes
        if boxes is None or boxes.id is None:
            return []
        names = result.names
        detections = []
        for xyxy, tid, cls, conf in zip(
            boxes.xyxy.tolist(), boxes.id.int().tolist(), boxes.cls.int().tolist(), boxes.conf.tolist()
        ):
            detections.append(Detection(tid, names[cls], conf, tuple(xyxy)))
        return detections

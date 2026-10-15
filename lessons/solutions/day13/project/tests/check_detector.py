import cv2
import numpy as np
from ultralytics.utils import ASSETS

from intelligence.config import load_config, project_path
from intelligence.detector import Detection, Detector, pick_device

cfg = load_config()

assert pick_device("cpu") == "cpu"  # a choice you make is respected
assert pick_device("auto") in ("cpu", "cuda", "mps")

model_path = project_path(cfg["paths"]["models"]) / cfg["model"]
detector = Detector(model_path, cfg["watch_classes"], cfg["confidence"], cfg["image_size"], "cpu")

# A class name the model does not know is reported at once, not silently ignored
try:
    Detector(model_path, ["person", "unicorn"], 0.45, 640, "cpu")
    raise AssertionError("an unknown class name should be rejected")
except ValueError as error:
    assert "unicorn" in str(error)

# A real photo: several persons and a bus
frame = cv2.imread(str(ASSETS / "bus.jpg"))
detections = detector.track(frame)
assert detections, "nothing found in the bus photo"
assert all(isinstance(d, Detection) for d in detections)
labels = [d.label for d in detections]
assert "bus" in labels and labels.count("person") >= 3, labels
assert all(d.label in cfg["watch_classes"] for d in detections)
assert all(d.confidence >= cfg["confidence"] for d in detections)
ids = [d.track_id for d in detections]
assert len(set(ids)) == len(ids), "every object needs its own track id"

# The same picture again: the tracker (persist=True) keeps the same ids
again = detector.track(frame)
assert sorted(d.track_id for d in again) == sorted(ids), "ids should stay the same for the same picture"

# A grey picture: nothing found, and the code must not crash on "no ids"
assert detector.track(np.full_like(frame, 114)) == []

print("detector OK")

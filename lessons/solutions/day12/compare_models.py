import os

# On Apple Silicon a few operations are missing on the GPU; let PyTorch run just those on the CPU.
# This must be set BEFORE torch is imported. (The project does the same in intelligence/__init__.py.)
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import time
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO
from ultralytics.utils import ASSETS


def pick_device():
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


Path("models").mkdir(exist_ok=True)
image = cv2.imread(str(ASSETS / "bus.jpg"))
best = pick_device()
devices = ["cpu"] if best == "cpu" else ["cpu", best]

for name in ("yolo11n.pt", "yolo11s.pt"):
    model = YOLO(f"models/{name}")  # downloaded the first time
    size_mb = Path(f"models/{name}").stat().st_size / 1e6
    for device in devices:
        model(image, device=device, verbose=False)  # warm-up: the very first call is always slower
        runs = 10
        start = time.perf_counter()
        for _ in range(runs):
            result = model(image, device=device, conf=0.5, verbose=False)[0]
        seconds = (time.perf_counter() - start) / runs
        print(f"{name} ({size_mb:4.1f} MB) on {device:4}: {seconds * 1000:5.1f} ms per picture "
              f"({1 / seconds:3.0f} FPS), {len(result.boxes)} objects")

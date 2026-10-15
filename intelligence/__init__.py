"""Security camera intelligence system: detection, tracking, memory, rules, alerts."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Keep ultralytics' settings inside the project instead of ~/Library/Application Support.
# This only affects this process and must be set before ultralytics is imported anywhere.
os.environ["YOLO_CONFIG_DIR"] = str(PROJECT_ROOT / ".ultralytics")
# On Apple Silicon a few ops (e.g. NMS) are missing on the GPU; run just those on the CPU.
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
# Windows: OpenCV's default camera backend can take 30+ seconds to open some webcams with this on.
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

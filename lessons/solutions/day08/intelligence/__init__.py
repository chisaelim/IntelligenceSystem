"""Security camera intelligence system: detection, tracking, memory, rules, alerts."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Windows: OpenCV's default camera backend can take 30+ seconds to open some webcams with this on.
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

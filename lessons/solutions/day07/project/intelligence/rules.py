from datetime import time

import numpy as np


def _parse_hm(text):
    """'22:00' -> datetime.time(22, 0)"""
    hour, minute = text.split(":")
    return time(int(hour), int(minute))


class RuleEngine:
    """Turns "a person is here" into "how much does it matter"."""

    def __init__(self, cfg, store=None):
        self.cfg = cfg
        self.store = store
        self.zones = [z for z in cfg["zones"] if z.get("enabled", True)]
        self.night_start = _parse_hm(cfg["night_hours"][0])
        self.night_end = _parse_hm(cfg["night_hours"][1])

    def is_night(self, now):
        t = now.time()
        if self.night_start > self.night_end:  # spans midnight, e.g. 22:00 -> 06:00
            return t >= self.night_start or t < self.night_end
        return self.night_start <= t < self.night_end

    def zone_polygons(self, frame_shape):
        """Each enabled zone as (name, polygon in pixels) for a frame of this shape."""
        h, w = frame_shape[:2]
        return [
            (z["name"], np.array([[x * w, y * h] for x, y in z["polygon"]], dtype=np.float32))
            for z in self.zones
        ]

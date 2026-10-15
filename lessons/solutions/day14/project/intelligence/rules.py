import time as time_module
from dataclasses import dataclass, field
from datetime import time

import cv2
import numpy as np

SEVERITY_NAMES = {0: "ignored", 1: "low", 2: "medium", 3: "HIGH"}
HISTORY_DAYS = 30
HISTORY_CACHE_SECONDS = 600


@dataclass
class Assessment:
    severity: int
    reasons: list = field(default_factory=list)

    def describe(self):
        return ", ".join(self.reasons)


def _parse_hm(text):
    hour, minute = text.split(":")
    return time(int(hour), int(minute))


class RuleEngine:
    """Turns "a person is here" into "how much does it matter", using zones, time and history."""

    def __init__(self, cfg, store=None):
        self.cfg = cfg
        self.store = store
        self.zones = [z for z in cfg["zones"] if z.get("enabled", True)]
        self.night_start = _parse_hm(cfg["night_hours"][0])
        self.night_end = _parse_hm(cfg["night_hours"][1])
        self._unusual_cache = {}  # (label, hour) -> (expires_at, is_unusual)

    def is_night(self, now):
        t = now.time()
        if self.night_start > self.night_end:  # spans midnight, e.g. 22:00 -> 06:00
            return t >= self.night_start or t < self.night_end
        return self.night_start <= t < self.night_end

    def zone_polygons(self, frame_shape):
        h, w = frame_shape[:2]
        return [
            (z["name"], np.array([[x * w, y * h] for x, y in z["polygon"]], dtype=np.float32))
            for z in self.zones
        ]

    def zones_for(self, label, box, frame_shape):
        """Names of zones containing the bottom-centre of the box (where the object touches the ground)."""
        x1, y1, x2, y2 = box
        foot = ((x1 + x2) / 2, y2)
        names = []
        for zone, (name, polygon) in zip(self.zones, self.zone_polygons(frame_shape)):
            if label in zone.get("watch", [label]) and cv2.pointPolygonTest(polygon, foot, False) >= 0:
                names.append(name)
        return names

    def is_unusual(self, label, now):
        """True if this label is rare at this hour compared with its own history."""
        anomaly = self.cfg["anomaly"]
        if not anomaly["enabled"] or self.store is None:  # no history to compare with
            return False
        key = (label, now.hour)
        cached = self._unusual_cache.get(key)
        if cached and cached[0] > time_module.monotonic():
            return cached[1]

        histogram = self.store.hour_histogram(label, HISTORY_DAYS)
        total = sum(histogram.values())
        unusual = total >= anomaly["min_history"] and histogram.get(now.hour, 0) / total < anomaly["rare_share"]
        self._unusual_cache[key] = (time_module.monotonic() + HISTORY_CACHE_SECONDS, unusual)
        return unusual

    def assess(self, label, zones, now):
        base = self.cfg["label_severity"].get(label, 1)
        if base == 0:
            return Assessment(0, [label])  # labels set to 0 are logged but never escalate

        score, reasons = base, [label]
        if self.is_night(now):
            score += 1
            reasons.append("at night")
        if zones:
            score += 1
            reasons.append("in " + ", ".join(sorted(zones)))
        if self.is_unusual(label, now):
            score += 1
            reasons.append("unusual for this hour")
        return Assessment(min(score, 3), reasons)


def should_alert(severity, alerted_severity, seconds_since_last_alert, alert_cfg):
    """The alert policy.

    An object causes an alert when it is serious enough, only once, and again only if it becomes
    more serious. Alerts are also spaced out by a cooldown, but a HIGH alert never waits.
    """
    worth_alerting = severity >= alert_cfg["min_severity"] and severity > alerted_severity
    cooled_down = seconds_since_last_alert >= alert_cfg["cooldown_seconds"] or severity == 3
    return worth_alerting and cooled_down

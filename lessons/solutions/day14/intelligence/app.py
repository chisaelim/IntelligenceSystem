import argparse
import time
from dataclasses import dataclass, field
from datetime import datetime

import cv2

from .config import load_config, project_path
from .events import EventStore
from .rules import SEVERITY_NAMES, RuleEngine, should_alert

SEVERITY_COLORS = {0: (160, 160, 160), 1: (0, 200, 0), 2: (0, 165, 255), 3: (0, 0, 255)}  # BGR


@dataclass
class Track:
    track_id: int
    label: str
    first_seen: float
    last_seen: float
    box: tuple = (0, 0, 0, 0)
    frames: int = 0
    confirmed: bool = False
    zones: set = field(default_factory=set)
    severity: int = 0
    alerted_severity: int = 0


def parse_source(value):
    """A camera number ("0" or 0) becomes an int. Anything else is a video file name."""
    return int(value) if str(value).isdigit() else value


def draw_overlay(frame, tracks, rules, now):
    for name, polygon in rules.zone_polygons(frame.shape):
        pts = polygon.astype("int32")
        cv2.polylines(frame, [pts], True, (255, 200, 0), 1)
        cv2.putText(frame, name, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)

    for t in tracks:
        x1, y1, x2, y2 = (int(v) for v in t.box)
        color = SEVERITY_COLORS[t.severity] if t.confirmed else (120, 120, 120)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2 if t.confirmed else 1)
        text = f"{t.label} #{t.track_id}"
        if t.zones:
            text += " [" + ",".join(sorted(t.zones)) + "]"
        cv2.putText(frame, text, (x1, max(y1 - 6, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    cv2.putText(frame, f"{now:%Y-%m-%d %H:%M:%S}", (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def main():
    ap = argparse.ArgumentParser(description="Webcam security camera")
    ap.add_argument("--source", help="camera index or video file (overrides config)")
    ap.add_argument("--no-window", action="store_true", help="run without the preview window")
    args = ap.parse_args()

    cfg = load_config()
    store = EventStore(project_path(cfg["paths"]["database"]))  # the rules read the history from it
    rules = RuleEngine(cfg, store)

    # Imported here so the program starts fast until it really needs the detector (loading PyTorch takes seconds).
    from .detector import Detector

    model_path = project_path(cfg["paths"]["models"]) / cfg["model"]
    model_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {model_path.name} ...")
    detector = Detector(model_path, cfg["watch_classes"], cfg["confidence"], cfg["image_size"], cfg["device"])

    source = parse_source(args.source if args.source is not None else cfg["source"])
    is_file = isinstance(source, str)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(
            f"Cannot open source {source!r}. For a camera on macOS, allow camera access for your "
            "terminal/VS Code in System Settings > Privacy & Security > Camera."
        )

    min_frames = cfg["min_track_frames"]
    lost_after = cfg["lost_seconds"]
    alert_cfg = cfg["alert"]
    tracks = {}  # track id -> Track
    last_alert = 0.0  # time.time() of the last alert

    def finish_track(t):
        if t.confirmed:
            print(f"[{datetime.now():%H:%M:%S}] {t.label} #{t.track_id} left after {t.last_seen - t.first_seen:.0f}s")

    print(f"Running on {detector.device}. Press q to quit.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                if is_file:
                    break
                print("Camera read failed, retrying...")
                time.sleep(0.5)
                continue

            now, clock = datetime.now(), time.monotonic()
            seen_ids = set()

            for det in detector.track(frame):
                seen_ids.add(det.track_id)
                t = tracks.get(det.track_id)
                if t is None:
                    t = tracks[det.track_id] = Track(det.track_id, det.label, clock, clock)
                t.last_seen, t.box, t.label = clock, det.box, det.label
                t.frames += 1

                if not t.confirmed and t.frames >= min_frames:
                    t.confirmed = True
                    t.zones.update(rules.zones_for(t.label, t.box, frame.shape))
                    a = rules.assess(t.label, t.zones, now)
                    print(f"[{now:%H:%M:%S}] {t.label} #{t.track_id} appeared ({SEVERITY_NAMES[a.severity]}: {a.describe()})")
                if not t.confirmed:
                    continue

                # Entering a zone is reported once per zone.
                for zone in set(rules.zones_for(t.label, t.box, frame.shape)) - t.zones:
                    t.zones.add(zone)
                    print(f"[{now:%H:%M:%S}] {t.label} #{t.track_id} entered {zone}")

                a = rules.assess(t.label, t.zones, now)
                t.severity = a.severity

                if should_alert(a.severity, t.alerted_severity, time.time() - last_alert, alert_cfg):
                    last_alert = time.time()
                    t.alerted_severity = a.severity
                    print(f"[{now:%H:%M:%S}] ALERT {SEVERITY_NAMES[a.severity]}: {a.describe()} "
                          f"({t.label} #{t.track_id})  [not sent yet]")

            lost = [tid for tid, t in tracks.items() if tid not in seen_ids and clock - t.last_seen > lost_after]
            for tid in lost:
                finish_track(tracks.pop(tid))

            if not args.no_window:
                draw_overlay(frame, [t for t in tracks.values() if t.track_id in seen_ids], rules, now)
                cv2.imshow("Security Camera", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        for t in tracks.values():
            finish_track(t)
        cap.release()
        cv2.destroyAllWindows()
        store.close()

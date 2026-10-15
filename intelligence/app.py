import argparse
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

import cv2

from . import PROJECT_ROOT
from .config import load_config, load_env, project_path
from .events import EventStore
from .rules import SEVERITY_NAMES, RuleEngine
from .telegram_bot import TelegramNotifier

SEVERITY_COLORS = {0: (160, 160, 160), 1: (0, 200, 0), 2: (0, 165, 255), 3: (0, 0, 255)}  # BGR
SEVERITY_ICONS = {1: "ℹ️", 2: "⚠️", 3: "🚨"}


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
    return int(value) if str(value).isdigit() else value


def print_history(store, limit):
    print("\nToday's summary (label: seen / alerts)")
    for label, seen, alerts in store.today_summary():
        print(f"  {label:12} {seen} / {alerts}")
    print(f"\nLast {limit} events")
    for ts, kind, label, track_id, zone, severity, alerted, detail in store.recent(limit):
        print(f"  {ts}  {kind:10} {label or '':10} #{track_id}  sev={severity}  {detail or ''}")


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
    ap = argparse.ArgumentParser(description="Webcam security camera with detection, memory and Telegram alerts")
    ap.add_argument("--config", help="path to a config json (default: config.json in the project)")
    ap.add_argument("--source", help="camera index or video file (overrides config)")
    ap.add_argument("--no-window", action="store_true", help="run without the preview window")
    ap.add_argument("--dry-run", action="store_true", help="print alerts instead of sending them to Telegram")
    ap.add_argument("--history", type=int, metavar="N", help="print today's summary and the last N events, then exit")
    args = ap.parse_args()

    # Alerts contain emoji; a redirected Windows console (cp1252) would raise on them.
    sys.stdout.reconfigure(errors="replace")

    cfg = load_config(args.config)
    store = EventStore(project_path(cfg["paths"]["database"]))

    if args.history:
        print_history(store, args.history)
        return

    env = load_env(PROJECT_ROOT / ".env")
    token, chat_id = env.get("TELEGRAM_BOT_TOKEN", ""), env.get("TELEGRAM_CHAT_ID", "")
    if not args.dry_run and (not token or not chat_id):
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the .env file (or use --dry-run).")

    # Imported here so --history stays instant (loading PyTorch takes a few seconds).
    from .detector import Detector

    snapshot_dir = project_path(cfg["paths"]["snapshots"])
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    model_path = project_path(cfg["paths"]["models"]) / cfg["model"]
    model_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {model_path.name} ...")
    detector = Detector(model_path, cfg["watch_classes"], cfg["confidence"], cfg["image_size"], cfg["device"])
    rules = RuleEngine(cfg, store)
    notifier = TelegramNotifier(token, chat_id, dry_run=args.dry_run)

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
    tracks = {}
    last_alert = 0.0

    notifier.send_text(f"Security camera started (device: {detector.device}).")
    print(f"Running on {detector.device}. Press q to quit.")

    def finish_track(t):
        if t.confirmed:
            store.add("left", t.track_id, t.label, severity=t.severity,
                      detail=f"seen {t.last_seen - t.first_seen:.0f}s")
            print(f"[{datetime.now():%H:%M:%S}] {t.label} #{t.track_id} left after {t.last_seen - t.first_seen:.0f}s")

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
                    store.add("appeared", t.track_id, t.label, ",".join(sorted(t.zones)) or None,
                              a.severity, detail=a.describe(), ts=now)
                    print(f"[{now:%H:%M:%S}] {t.label} #{t.track_id} appeared ({SEVERITY_NAMES[a.severity]}: {a.describe()})")
                if not t.confirmed:
                    continue

                for zone in set(rules.zones_for(t.label, t.box, frame.shape)) - t.zones:
                    t.zones.add(zone)
                    store.add("zone_enter", t.track_id, t.label, zone, t.severity, ts=now)
                    print(f"[{now:%H:%M:%S}] {t.label} #{t.track_id} entered {zone}")

                a = rules.assess(t.label, t.zones, now)
                t.severity = a.severity

                # Alert once per track, and again only if it becomes more serious.
                worth_alerting = a.severity >= alert_cfg["min_severity"] and a.severity > t.alerted_severity
                cooled_down = time.time() - last_alert >= alert_cfg["cooldown_seconds"] or a.severity == 3
                if worth_alerting and cooled_down:
                    last_alert = time.time()
                    t.alerted_severity = a.severity

                    annotated = frame.copy()
                    draw_overlay(annotated, [x for x in tracks.values() if x.track_id in seen_ids], rules, now)
                    path = snapshot_dir / f"{now:%Y%m%d_%H%M%S}_{t.label}_{t.track_id}.jpg"
                    cv2.imwrite(str(path), annotated)

                    store.add("alert", t.track_id, t.label, ",".join(sorted(t.zones)) or None,
                              a.severity, alerted=True, snapshot=str(path), detail=a.describe(), ts=now)
                    notifier.send_photo(
                        path, f"{SEVERITY_ICONS[a.severity]} {SEVERITY_NAMES[a.severity]}: {a.describe()}\n"
                              f"{now:%Y-%m-%d %H:%M:%S}  ({t.label} #{t.track_id})")

            for tid in [tid for tid, t in tracks.items() if tid not in seen_ids and clock - t.last_seen > lost_after]:
                finish_track(tracks.pop(tid))

            if not args.no_window:
                draw_overlay(frame, [x for x in tracks.values() if x.track_id in seen_ids], rules, now)
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
        notifier.send_text("Security camera stopped.")
        notifier.flush()
        store.close()

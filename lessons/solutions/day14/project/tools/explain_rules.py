"""Ask the rule engine how serious a pretend sighting would be, without waiting for the right time of day.

    python -m tools.explain_rules --label person --hour 3
    python -m tools.explain_rules --label person --hour 23 --zone front_door
    python -m tools.explain_rules --label car --hour 12 --db data/events.db
"""
import argparse
from datetime import datetime

from intelligence.config import load_config, project_path
from intelligence.events import EventStore
from intelligence.rules import SEVERITY_NAMES, RuleEngine


def main():
    ap = argparse.ArgumentParser(description="Explain the severity of a pretend sighting")
    ap.add_argument("--label", default="person")
    ap.add_argument("--hour", type=int, default=12, help="hour of the day, 0 to 23")
    ap.add_argument("--zone", action="append", default=[], help="a zone the object is in (can be repeated)")
    ap.add_argument("--db", default="data/demo_events.db", help="the history to compare with")
    args = ap.parse_args()

    path = project_path(args.db)
    if not path.is_file():
        raise SystemExit(f"History file not found: {path}. Create one with: python -m tools.seed_history")

    engine = RuleEngine(load_config(), EventStore(path))
    when = datetime.now().replace(hour=args.hour, minute=0, second=0, microsecond=0)
    assessment = engine.assess(args.label, set(args.zone), when)
    print(f"{args.label} at {args.hour:02d}:00 -> {SEVERITY_NAMES[assessment.severity]} "
          f"({assessment.severity}): {assessment.describe()}")


if __name__ == "__main__":
    main()

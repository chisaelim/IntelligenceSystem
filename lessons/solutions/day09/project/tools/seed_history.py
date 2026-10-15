"""Fill a database with PRETEND daytime sightings, so the "unusual for this hour" rule can be tested.

    python -m tools.seed_history                    -> data/demo_events.db (20 days, 5 sightings a day)
    python -m tools.seed_history --days 30 --per-day 8 --replace
"""
import argparse
import random
from datetime import datetime, timedelta

from intelligence.config import project_path
from intelligence.events import EventStore


def main():
    ap = argparse.ArgumentParser(description="Fill a database with pretend daytime sightings")
    ap.add_argument("--db", default="data/demo_events.db", help="database file to create")
    ap.add_argument("--days", type=int, default=20, help="how many past days to fill")
    ap.add_argument("--per-day", type=int, default=5, help="sightings per day")
    ap.add_argument("--label", default="person")
    ap.add_argument("--first-hour", type=int, default=8)
    ap.add_argument("--last-hour", type=int, default=17)
    ap.add_argument("--seed", type=int, default=1, help="same seed = same pretend history")
    ap.add_argument("--replace", action="store_true", help="delete the file first if it exists")
    args = ap.parse_args()

    path = project_path(args.db)
    if path.exists():
        if not args.replace:
            raise SystemExit(f"{path} already exists. Use --replace to delete it first.")
        path.unlink()

    random.seed(args.seed)
    store = EventStore(path)
    now = datetime.now()
    count = 0
    for days_ago in range(1, args.days + 1):
        for _ in range(args.per_day):
            when = (now - timedelta(days=days_ago)).replace(
                hour=random.randint(args.first_hour, args.last_hour),
                minute=random.randint(0, 59),
                second=0,
                microsecond=0,
            )
            count += 1
            store.add("appeared", track_id=count, label=args.label, severity=2, ts=when)
    store.close()
    print(f"Saved {count} pretend '{args.label}' sightings between {args.first_hour}:00 and "
          f"{args.last_hour}:59 to {path}")


if __name__ == "__main__":
    main()

"""Chart: how many sightings in each hour of the day.

    python -m tools.plot_hours data/demo_events.db
"""
import argparse
import sqlite3

import matplotlib

matplotlib.use("Agg")  # draw into a file: no window needed
import matplotlib.pyplot as plt
import pandas as pd

from intelligence.config import project_path


def main():
    ap = argparse.ArgumentParser(description="Chart of sightings per hour of the day")
    ap.add_argument("db", nargs="?", default="data/demo_events.db", help="database file")
    ap.add_argument("--label", default="person")
    ap.add_argument("--out", default="output/sightings_per_hour.png")
    args = ap.parse_args()

    path = project_path(args.db)
    if not path.is_file():
        raise SystemExit(f"Database file not found: {path}")

    db = sqlite3.connect(path)
    query = (
        "SELECT CAST(strftime('%H', ts) AS INTEGER) AS hour, COUNT(*) AS sightings "
        "FROM events WHERE kind = 'appeared' AND label = ? GROUP BY hour"
    )
    table = pd.read_sql(query, db, params=(args.label,))
    db.close()
    if table.empty:
        raise SystemExit(f"No 'appeared' events for label {args.label!r} in {path}")

    per_hour = table.set_index("hour")["sightings"].reindex(range(24), fill_value=0)

    ax = per_hour.plot.bar(color="#2a7de1", figsize=(9, 3.5))
    ax.set_xlabel("hour of the day")
    ax.set_ylabel("sightings")
    ax.set_title(f"'{args.label}' sightings per hour ({per_hour.sum()} in total)")
    plt.tight_layout()

    out = project_path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=100)

    quiet = [hour for hour in range(24) if per_hour[hour] == 0]
    print(f"{per_hour.sum()} sightings. Busiest hour: {per_hour.idxmax()}:00 ({per_hour.max()} sightings)")
    print("Hours with no sightings:", quiet)
    print("Chart saved to", out)


if __name__ == "__main__":
    main()

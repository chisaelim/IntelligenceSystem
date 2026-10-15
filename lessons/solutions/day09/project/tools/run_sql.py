"""Run one SQL statement on a SQLite file and print the result as a table.

    python -m tools.run_sql data/practice.db "SELECT * FROM sightings LIMIT 5"
"""
import sqlite3
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: python -m tools.run_sql data/events.db "SELECT * FROM events LIMIT 5"')
    database, query = sys.argv[1], sys.argv[2]
    if not Path(database).is_file():
        raise SystemExit(f"Database file not found: {database}")

    db = sqlite3.connect(database)
    cursor = db.execute(query)
    if cursor.description is None:  # INSERT, UPDATE, DELETE ... have no table to show
        db.commit()
        print("OK")
        return

    names = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    widths = [max(len(str(value)) for value in [name] + [row[i] for row in rows]) for i, name in enumerate(names)]
    print("  ".join(name.ljust(width) for name, width in zip(names, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(str(value).ljust(width) for value, width in zip(row, widths)))
    print(f"({len(rows)} rows)")


if __name__ == "__main__":
    main()

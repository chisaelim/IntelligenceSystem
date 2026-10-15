import sqlite3
from pathlib import Path

Path("data").mkdir(exist_ok=True)
Path("data/practice.db").unlink(missing_ok=True)  # start fresh every time

db = sqlite3.connect("data/practice.db")
db.execute(
    """
    CREATE TABLE sightings (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        ts         TEXT NOT NULL,
        label      TEXT NOT NULL,
        confidence REAL
    )
    """
)

rows = [
    ("2026-03-12T08:15:00", "person", 0.91),
    ("2026-03-12T08:40:00", "car", 0.84),
    ("2026-03-12T12:05:00", "person", 0.77),
    ("2026-03-12T12:07:00", "person", 0.88),
    ("2026-03-12T18:30:00", "dog", 0.69),
    ("2026-03-12T23:10:00", "person", 0.62),
    ("2026-03-13T02:45:00", "person", 0.55),
    ("2026-03-13T08:20:00", "bicycle", 0.73),
    ("2026-03-13T08:22:00", "person", 0.93),
    ("2026-03-13T14:00:00", "car", 0.81),
    ("2026-03-13T17:50:00", "person", 0.86),
    ("2026-03-14T08:10:00", "person", 0.95),
    ("2026-03-14T12:30:00", "cat", 0.58),
    ("2026-03-14T21:15:00", "person", 0.79),
]
db.executemany("INSERT INTO sightings (ts, label, confidence) VALUES (?, ?, ?)", rows)
db.commit()
db.close()
print(f"Created data/practice.db with {len(rows)} sightings")

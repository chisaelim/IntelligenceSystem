import sqlite3
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT    NOT NULL,   -- local time, ISO 8601
    kind      TEXT    NOT NULL,   -- appeared | zone_enter | alert | left
    track_id  INTEGER,
    label     TEXT,
    zone      TEXT,
    severity  INTEGER NOT NULL DEFAULT 0,
    alerted   INTEGER NOT NULL DEFAULT 0,
    snapshot  TEXT,
    detail    TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events (ts);
CREATE INDEX IF NOT EXISTS idx_events_label_kind ON events (label, kind);
"""


class EventStore:
    """The system's memory: everything it has seen, in a local SQLite file."""

    def __init__(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)
        self.db.commit()

    def add(self, kind, track_id=None, label=None, zone=None, severity=0,
            alerted=False, snapshot=None, detail=None, ts=None):
        ts = (ts or datetime.now()).isoformat(timespec="seconds")
        cur = self.db.execute(
            "INSERT INTO events (ts, kind, track_id, label, zone, severity, alerted, snapshot, detail) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ts, kind, track_id, label, zone, severity, int(alerted), snapshot, detail),
        )
        self.db.commit()
        return cur.lastrowid

    def recent(self, limit=20):
        return self.db.execute(
            "SELECT ts, kind, label, track_id, zone, severity, alerted, detail "
            "FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def today_summary(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.db.execute(
            "SELECT label, SUM(kind = 'appeared'), SUM(kind = 'alert') FROM events "
            "WHERE kind IN ('appeared', 'alert') AND ts >= ? GROUP BY label ORDER BY 2 DESC",
            (today,),
        ).fetchall()

    def close(self):
        self.db.close()

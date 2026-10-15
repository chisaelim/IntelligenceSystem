import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from intelligence.events import EventStore

with tempfile.TemporaryDirectory() as folder:
    store = EventStore(Path(folder) / "sub" / "events.db")  # also creates the folder "sub"

    store.add("appeared", track_id=1, label="person", severity=2, detail="person")
    store.add("zone_enter", track_id=1, label="person", zone="front_door", severity=3)
    store.add("alert", track_id=1, label="person", severity=3, alerted=True, snapshot="a.jpg")
    store.add("appeared", track_id=2, label="car", severity=1)
    store.add("left", track_id=1, label="person", severity=3, detail="seen 12s")

    rows = store.recent(3)
    assert len(rows) == 3
    assert rows[0][1] == "left"  # newest first
    assert rows[0][7] == "seen 12s"

    summary = store.today_summary()
    assert ("person", 1, 1) in summary  # 1 appeared, 1 alert
    assert ("car", 1, 0) in summary

    # An event from yesterday is not in today's summary
    store.add("appeared", track_id=3, label="dog", severity=0, ts=datetime.now() - timedelta(days=1))
    assert not any(label == "dog" for label, _, _ in store.today_summary())

    store.close()

print("events OK")

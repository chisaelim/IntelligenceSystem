from intelligence.rules import should_alert

alert_cfg = {"min_severity": 2, "cooldown_seconds": 30}
LONG_AGO = 10_000  # seconds since the last alert

# Below the minimum severity: never an alert
assert not should_alert(1, 0, LONG_AGO, alert_cfg)
assert not should_alert(0, 0, LONG_AGO, alert_cfg)

# The first alert of a track
assert should_alert(2, 0, LONG_AGO, alert_cfg)

# The same track, same severity: only once
assert not should_alert(2, 2, LONG_AGO, alert_cfg)

# The track becomes more serious: alert again
assert should_alert(3, 2, LONG_AGO, alert_cfg)

# Cooldown: another alert 5 seconds after the last one is held back ...
assert not should_alert(2, 0, 5, alert_cfg)
# ... unless it is HIGH
assert should_alert(3, 0, 5, alert_cfg)

# Exactly at the end of the cooldown
assert should_alert(2, 0, 30, alert_cfg)
assert not should_alert(2, 0, 29.9, alert_cfg)

print("policy OK")

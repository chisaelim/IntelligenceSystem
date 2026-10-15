import json

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

LABEL_SEVERITY = cfg["label_severity"]  # the dictionary now comes from the file


def assess(label, at_night=False, in_zones=()):
    """Return (severity, reasons). Severity is 0 to 3."""
    base = LABEL_SEVERITY.get(label, 1)
    if base == 0:
        return 0, [label]

    score = base
    reasons = [label]
    if at_night:
        score += 1
        reasons.append("at night")
    if in_zones:
        score += 1
        reasons.append("in " + ", ".join(sorted(in_zones)))
    return min(score, 3), reasons


for label in ("person", "bus", "cat"):
    severity, reasons = assess(label, at_night=True)
    print(f"{label:7} at night -> {severity} ({', '.join(reasons)})")

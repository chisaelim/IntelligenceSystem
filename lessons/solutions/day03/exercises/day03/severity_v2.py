LABEL_SEVERITY = {
    "person": 2,
    "car": 1, "truck": 1, "bus": 1, "motorcycle": 1, "bicycle": 1,
    "dog": 0, "cat": 0,
}


def assess(label, at_night=False, in_zones=()):
    """Return (severity, reasons). Severity is 0 to 3."""
    base = LABEL_SEVERITY.get(label, 1)  # unknown labels count as 1
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


severity, reasons = assess("person", at_night=True, in_zones={"front_door"})
print(severity, "-", ", ".join(reasons))

severity, reasons = assess("dog", at_night=True)
print(severity, "-", ", ".join(reasons))

severity, reasons = assess("suitcase")
print(severity, "-", ", ".join(reasons))

def base_severity(label):
    """How serious is this kind of object on its own? 0 means 'log it, never alert'."""
    if label == "person":
        return 2
    elif label in ("car", "truck", "bus", "motorcycle", "bicycle"):
        return 1
    else:
        return 0


def assess(label, at_night=False, in_zone=False):
    """Return a severity from 0 to 3."""
    score = base_severity(label)
    if score == 0:
        return 0
    if at_night:
        score = score + 1
    if in_zone:
        score = score + 1
    return min(score, 3)


def severity_name(severity):
    if severity == 0:
        return "ignored"
    elif severity == 1:
        return "low"
    elif severity == 2:
        return "medium"
    else:
        return "HIGH"


# Quick checks. If one of them is wrong, Python stops with an AssertionError.
assert assess("person") == 2
assert assess("person", at_night=True) == 3
assert assess("car") == 1
assert assess("car", at_night=True, in_zone=True) == 3
assert assess("dog", at_night=True, in_zone=True) == 0
assert assess("person", at_night=True, in_zone=True) == 3  # capped at 3

print("person, daytime  :", severity_name(assess("person")))
print("person, at night :", severity_name(assess("person", at_night=True)))
print("car, daytime     :", severity_name(assess("car")))
print("car, night + zone:", severity_name(assess("car", at_night=True, in_zone=True)))
print("dog, anything    :", severity_name(assess("dog", at_night=True, in_zone=True)))

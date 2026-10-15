# Each detection is a tuple: (label, confidence, (x1, y1, x2, y2))
detections = [
    ("bus", 0.94, (4, 229, 796, 728)),
    ("person", 0.89, (671, 395, 810, 879)),
    ("person", 0.88, (47, 400, 239, 904)),
    ("person", 0.86, (223, 409, 344, 860)),
    ("person", 0.62, (0, 556, 69, 872)),
    ("person", 0.31, (120, 100, 160, 180)),  # a weak guess
]

MIN_CONFIDENCE = 0.45

# Keep only the confident detections
confident = [d for d in detections if d[1] >= MIN_CONFIDENCE]
print("kept", len(confident), "of", len(detections), "detections")

# Only the persons
persons = [d for d in confident if d[0] == "person"]
print("persons:", len(persons))

# Just the labels
labels = [label for label, confidence, box in confident]
print("labels:", labels)

# The most confident detection
best = max(confident, key=lambda d: d[1])
print("best:", best[0], best[1])

# Size of each person box
for label, confidence, (x1, y1, x2, y2) in persons:
    width = x2 - x1
    height = y2 - y1
    print(f"{label} {confidence:.2f}: width={width}, height={height}, area={width * height:,}")

# The three largest boxes
def box_area(detection):
    x1, y1, x2, y2 = detection[2]
    return (x2 - x1) * (y2 - y1)


largest = sorted(confident, key=box_area, reverse=True)[:3]
print("largest three:", [d[0] for d in largest])

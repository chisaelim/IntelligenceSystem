detections = [("person", 0.9), ("car", 0.8), ("person", 0.7), ("person", 0.5), ("car", 0.6)]

# Group the confidences by label: {"person": [0.9, 0.7, 0.5], "car": [0.8, 0.6]}
groups = {}
for label, confidence in detections:
    if label not in groups:
        groups[label] = []
    groups[label].append(confidence)

for label, values in groups.items():
    average = sum(values) / len(values)
    print(f"{label}: {len(values)} detections, average confidence {average:.2f}")

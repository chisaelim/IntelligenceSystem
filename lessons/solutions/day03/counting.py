sightings = ["person", "car", "person", "dog", "person", "car", "bicycle", "person"]

counts = {}
for label in sightings:
    counts[label] = counts.get(label, 0) + 1

for label, number in counts.items():
    print(f"{label}: {number}")

most_common = max(counts, key=counts.get)
print("most common:", most_common)

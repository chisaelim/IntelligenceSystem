class SightingCounter:
    """Counts how many times each label was seen."""

    def __init__(self):
        self.counts = {}

    def add(self, label):
        self.counts[label] = self.counts.get(label, 0) + 1

    def total(self):
        return sum(self.counts.values())

    def most_common(self):
        return max(self.counts, key=self.counts.get)


counter = SightingCounter()
for label in ["person", "car", "person", "person", "dog"]:
    counter.add(label)

print("total sightings:", counter.total())
print("most common:", counter.most_common())
print("counts:", counter.counts)

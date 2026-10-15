detections = [("person", 0.9), ("car", 0.8), ("person", 0.7), ("person", 0.5)]


def average_confidence(items, label):
    total = 0
    count = 0
    for name, confidence in items:
        if name == label:
            total += confidence
            count += 1  # count only the items we added
    return total / count


average = average_confidence(detections, "person")
print("average person confidence:", round(average, 2))  # 0.7

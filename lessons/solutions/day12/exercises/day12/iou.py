def box_area(box):
    x1, y1, x2, y2 = box
    return max(0, x2 - x1) * max(0, y2 - y1)


def iou(a, b):
    """Intersection over Union: 0 = the boxes do not touch, 1 = identical boxes."""
    overlap = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    intersection = box_area(overlap)
    union = box_area(a) + box_area(b) - intersection
    return intersection / union if union else 0.0


def nms(detections, threshold=0.5):
    """Non-maximum suppression: keep the best box, drop boxes that overlap a kept box too much."""
    keep = []
    for detection in sorted(detections, key=lambda d: d[1], reverse=True):
        if all(iou(detection[2], kept[2]) < threshold for kept in keep):
            keep.append(detection)
    return keep


assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0  # the same box
assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0  # far apart
assert abs(iou((0, 0, 10, 10), (5, 0, 15, 10)) - 1 / 3) < 1e-9  # half overlap: 50 / (100 + 100 - 50)

detections = [
    ("person", 0.90, (100, 100, 200, 300)),
    ("person", 0.85, (105, 98, 205, 305)),  # the same person, found a second time
    ("person", 0.80, (400, 120, 480, 320)),  # a different person
]
print("IoU of the two boxes on the first person:", round(iou(detections[0][2], detections[1][2]), 2))
print("IoU of person 1 and person 2:", round(iou(detections[0][2], detections[2][2]), 2))

kept = nms(detections)
print("kept", len(kept), "of", len(detections), "boxes:")
for label, confidence, box in kept:
    print(f"  {label} {confidence:.2f} {box}")

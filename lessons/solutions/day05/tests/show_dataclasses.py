from intelligence.app import Track
from intelligence.detector import Detection

detection = Detection(track_id=1, label="person", confidence=0.91, box=(47, 400, 239, 904))
print(detection)

a = Track(track_id=1, label="person", first_seen=0.0, last_seen=0.0)
b = Track(track_id=2, label="car", first_seen=0.0, last_seen=0.0)
a.zones.add("front_door")
print(a)
print("b has its own empty set of zones:", b.zones == set())

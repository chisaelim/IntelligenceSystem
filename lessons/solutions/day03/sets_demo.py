# Track ids seen in three frames in a row
frame_1 = [1, 2, 3]
frame_2 = [2, 3, 3, 4]  # 3 is listed twice by mistake
frame_3 = [3, 4, 5]

seen = set()
for frame in (frame_1, frame_2, frame_3):
    seen = seen | set(frame)
print("unique track ids:", sorted(seen))

# Which zones is a track in now, and which did it already know about?
known_zones = {"front_door"}
current_zones = {"front_door", "driveway"}
new_zones = current_zones - known_zones
print("new zones:", new_zones)

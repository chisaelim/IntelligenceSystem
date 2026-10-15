FPS = 30
SECONDS = 3

for frame_number in range(1, FPS * SECONDS + 1):
    if frame_number % FPS == 0:
        print(f"{frame_number // FPS} second(s) passed, {frame_number} frames read")

import time

FRAME_TIME = 0.05  # a "camera" that makes 20 frames per second


def send_alert_slowly():
    """Pretend network call: the server needs 2 seconds to answer."""
    time.sleep(2.0)


last_frame = time.perf_counter()
longest_gap = 0.0

for frame_number in range(1, 61):  # 3 seconds of video
    time.sleep(FRAME_TIME)  # waiting for the camera
    now = time.perf_counter()
    longest_gap = max(longest_gap, now - last_frame)
    last_frame = now

    if frame_number == 5:
        print("frame 5: something happened, sending an alert...")
        send_alert_slowly()  # the whole program waits here!
        print("   (alert sent)")

print(f"longest pause between two frames: {longest_gap:.2f} seconds")

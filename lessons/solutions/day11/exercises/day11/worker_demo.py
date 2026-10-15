import queue
import threading
import time

FRAME_TIME = 0.05  # a "camera" that makes 20 frames per second
alerts = queue.Queue()


def send_alert_slowly(text):
    """Pretend network call: the server needs 2 seconds to answer."""
    time.sleep(2.0)
    print(f"   (alert sent: {text})")


def worker():
    while True:
        text = alerts.get()  # waits here until there is something to send
        send_alert_slowly(text)


threading.Thread(target=worker, daemon=True).start()

last_frame = time.perf_counter()
longest_gap = 0.0

for frame_number in range(1, 61):  # 3 seconds of video
    time.sleep(FRAME_TIME)  # waiting for the camera
    now = time.perf_counter()
    longest_gap = max(longest_gap, now - last_frame)
    last_frame = now

    if frame_number == 5:
        print("frame 5: something happened, queueing an alert...")
        alerts.put("person at the door")  # takes almost no time, the loop goes on

print(f"longest pause between two frames: {longest_gap:.2f} seconds")

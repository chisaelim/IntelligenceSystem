import time

MAX_ATTEMPTS = 5


def read_frame(attempt):
    """Pretend camera: the first two reads fail, the third works."""
    return attempt >= 3


got_frame = False
attempt = 0
while attempt < MAX_ATTEMPTS and not got_frame:
    attempt += 1
    got_frame = read_frame(attempt)
    if not got_frame:
        print(f"Camera read failed (attempt {attempt}), retrying...")
        time.sleep(0.2)

if got_frame:
    print(f"Got a frame after {attempt} attempt(s)")
else:
    print("Camera did not respond, giving up")

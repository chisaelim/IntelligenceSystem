import cv2
import numpy as np

WIDTH, HEIGHT, FPS = 320, 240, 15
writer = cv2.VideoWriter("motion_test.mp4", cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT))


def scene(brightness, square_x=None):
    """A grey room, with an optional white square (a "person") at the given x position."""
    frame = np.full((HEIGHT, WIDTH, 3), brightness, np.uint8)
    if square_x is not None:
        cv2.rectangle(frame, (square_x, 100), (square_x + 40, 140), (255, 255, 255), -1)
    return frame


for _ in range(10):  # frames 0-9:    the room is empty
    writer.write(scene(90))
for i in range(30):  # frames 10-39:  a square walks across the picture
    writer.write(scene(90, 10 + i * 8))
for _ in range(15):  # frames 40-54:  the square stands still
    writer.write(scene(90, 10 + 29 * 8))
for _ in range(15):  # frames 55-69:  the square has left, the room is empty
    writer.write(scene(90))
for _ in range(30):  # frames 70-99:  somebody switches the light on: nothing moves, but it is brighter
    writer.write(scene(150))

writer.release()
print("saved motion_test.mp4 (100 frames)")

import cv2
from ultralytics.utils import ASSETS

image = cv2.imread(str(ASSETS / "bus.jpg"))
if image is None:  # imread does not raise an error when it fails, it returns None
    raise SystemExit("Could not read the image")

cv2.imshow("Bus", image)
print("Click on the picture window, then press any key to close it.")
cv2.waitKey(0)
cv2.destroyAllWindows()

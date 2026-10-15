import sys

print("Python:", sys.version.split()[0])

import numpy
import cv2
import torch
import ultralytics
import requests
import pandas

print("numpy:", numpy.__version__)
print("opencv:", cv2.__version__)
print("torch:", torch.__version__)
print("ultralytics:", ultralytics.__version__)
print("requests:", requests.__version__)
print("pandas:", pandas.__version__)
print("GPU available:", torch.cuda.is_available() or torch.backends.mps.is_available())
print("Everything is installed. You are ready!")

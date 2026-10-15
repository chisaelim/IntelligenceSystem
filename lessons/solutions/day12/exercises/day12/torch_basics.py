import time

import numpy as np
import torch

print("torch version:", torch.__version__)

x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print("tensor:", x.tolist(), "| shape:", tuple(x.shape), "| type:", x.dtype)
print("x * 2 =", (x * 2).tolist())
print("x @ x =", (x @ x).tolist(), "(matrix multiplication)")

# NumPy and PyTorch work together
array = np.array([1, 2, 3])
tensor = torch.from_numpy(array)
print("from NumPy:", tensor.tolist(), "| back to NumPy:", tensor.numpy().tolist())


def pick_device(preference="auto"):
    if preference != "auto":
        return preference
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


device = pick_device()
print("best device on this computer:", device)


def synchronize(device):
    """GPUs work in the background; wait until they are really finished before reading the clock."""
    if device == "cuda":
        torch.cuda.synchronize()
    elif device == "mps":
        torch.mps.synchronize()


def seconds_per_multiplication(device, size=2000, repeats=5):
    a = torch.rand(size, size, device=device)
    b = torch.rand(size, size, device=device)
    a @ b  # warm-up
    synchronize(device)
    start = time.perf_counter()
    for _ in range(repeats):
        a @ b
    synchronize(device)
    return (time.perf_counter() - start) / repeats


cpu = seconds_per_multiplication("cpu")
print(f"2000 x 2000 matrix multiplication on the cpu: {cpu * 1000:.0f} ms")
if device != "cpu":
    gpu = seconds_per_multiplication(device)
    print(f"2000 x 2000 matrix multiplication on {device}: {gpu * 1000:.0f} ms ({cpu / gpu:.0f} times faster)")

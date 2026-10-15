import time

import numpy as np

size = 1_000_000
numbers = list(range(size))  # a Python list
array = np.arange(size)  # a NumPy array with the same numbers

start = time.perf_counter()
squares = [n * n for n in numbers]
list_time = time.perf_counter() - start

start = time.perf_counter()
squares_np = array * array
numpy_time = time.perf_counter() - start

print(f"Python list: {list_time * 1000:.1f} ms")
print(f"NumPy array: {numpy_time * 1000:.1f} ms")
print(f"NumPy is about {list_time / numpy_time:.0f} times faster")

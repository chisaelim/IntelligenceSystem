# Day 6: NumPy and images as arrays

**Hours 16-18 of 45** · Project milestone: none to commit today, but you finish with the exact NumPy idea that turns a zone from `config.json` into pixels

## What you can do at the end of today

- Create NumPy arrays and read their `shape`, `dtype` and `size`.
- Pick values with indexing, slicing and **boolean masks**.
- Calculate with whole arrays at once (vectorising) and understand **broadcasting**.
- Explain why a picture is just an array of numbers, and read, crop, flip and brighten one.
- Avoid the `uint8` overflow bug.

## Where today fits in the project

Everything the camera sees is an array. A frame from the webcam is a NumPy array of shape `(height, width, 3)`. OpenCV (Day 7), YOLO (Day 12) and the drawing code all give you arrays and expect arrays. If you can slice and calculate with arrays, the rest of Week 2 and 3 becomes much easier.

Today ends with the one NumPy line the project uses to turn the zone corners in `config.json` (fractions from 0 to 1) into pixel positions.

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 16 | 5 | Warm-up: commit check from Day 5 (`git log --oneline`) |
| | 20 | Talk: why NumPy, arrays, shape, dtype, indexing, slicing |
| | 10 | Live demo in the console |
| | 25 | **Lab 6.1** Array practice |
| 17 | 15 | Talk: vectorising, aggregates, broadcasting |
| | 10 | Live demo |
| | 15 | **Lab 6.2** Speed race: list vs array |
| | 20 | **Lab 6.3** Broadcasting practice |
| 18 | 15 | Talk: a picture is an array |
| | 10 | Live demo |
| | 35 | **Labs 6.4-6.6** Read, crop, flip, brighten, zone polygon |

You can do the console parts in the Python console (type `python`) or in a JupyterLab notebook. The notebook is nicer here because it shows the result of each line.

---

# Hour 16: Arrays

## Learn

**NumPy** is a free library for working with numbers in bulk. A NumPy **array** looks like a list but is stored compactly and every item has the **same type**. This makes it many times faster than a Python list for maths (often 10 to 100 times), and it is the base of every AI library.

By convention we import it as `np`:

```pycon
>>> import numpy as np
>>> a = np.array([1, 2, 3, 4])
>>> a
array([1, 2, 3, 4])
>>> a.shape
(4,)
>>> a.dtype
dtype('int64')
>>> a * 2
array([2, 4, 6, 8])
```

- **`shape`** is the size in each direction, as a tuple. `(4,)` means one direction with 4 items.
- **`dtype`** is the type of every item (`int64`, `float64`, `uint8`, ...).
- A `list * 2` repeats the list. An array `* 2` multiplies **each number**. This is the key idea of NumPy.

### Two-dimensional arrays

A table of numbers is a 2D array. The first number of the shape is the number of **rows**, the second the number of **columns**:

```pycon
>>> import numpy as np
>>> b = np.array([[1, 2, 3], [4, 5, 6]])
>>> b
array([[1, 2, 3],
       [4, 5, 6]])
>>> b.shape
(2, 3)
>>> b.ndim
2
>>> b.size
6
>>> b[0]
array([1, 2, 3])
>>> b[1, 2]
np.int64(6)
>>> b[:, 1]
array([2, 5])
>>> b[0, 1:]
array([2, 3])
```

Reading the indexes: `b[1, 2]` is "row 1, column 2". `b[:, 1]` is "all rows, column 1". `b[0, 1:]` is "row 0, columns from 1 to the end". The colon `:` means "everything in this direction".

### Making arrays

```pycon
>>> import numpy as np
>>> np.zeros((2, 3))
array([[0., 0., 0.],
       [0., 0., 0.]])
>>> np.ones(3, dtype=np.uint8)
array([1, 1, 1], dtype=uint8)
>>> np.arange(0, 10, 2)
array([0, 2, 4, 6, 8])
>>> np.linspace(0, 1, 5)
array([0.  , 0.25, 0.5 , 0.75, 1.  ])
>>> np.arange(12).reshape(3, 4)
array([[ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11]])
```

### Boolean masks

Comparing an array with a number gives an array of `True`/`False`. Use it as a **mask** to pick values, like a filter:

```pycon
>>> import numpy as np
>>> confidence = np.array([0.91, 0.30, 0.62, 0.88])
>>> confidence > 0.5
array([ True, False,  True,  True])
>>> confidence[confidence > 0.5]
array([0.91, 0.62, 0.88])
>>> (confidence > 0.5).sum()
np.int64(3)
>>> confidence.mean()
np.float64(0.6775)
```

(`np.float64(0.6775)` is just a NumPy number. Treat it as `0.6775`.) `.sum()` on a mask counts the `True` values, because `True` counts as 1.

## Lab 6.1: Array practice

Open a notebook (or the console). Using only what you learned, do these. Try each one before you open the answers.

1. Make a 3 x 4 array with the numbers 0 to 11.
2. Print its shape.
3. Get the second row.
4. Get the last column.
5. Get all values greater than 5.
6. Count how many values are even.

<details><summary>Answers</summary>

```pycon
>>> import numpy as np
>>> grid = np.arange(12).reshape(3, 4)
>>> grid
array([[ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11]])
>>> grid.shape
(3, 4)
>>> grid[1]
array([4, 5, 6, 7])
>>> grid[:, -1]
array([ 3,  7, 11])
>>> grid[grid > 5]
array([ 6,  7,  8,  9, 10, 11])
>>> (grid % 2 == 0).sum()
np.int64(6)
```

</details>

## Check yourself

1. What is the shape of `np.zeros((2, 5))`?
2. What does `a[:, 0]` mean for a 2D array `a`?
3. Why must all items of an array have the same type?

<details><summary>Answers</summary>

1. `(2, 5)`: 2 rows and 5 columns.
2. All rows, column 0: the first column.
3. Because the numbers are stored in one block of memory with a fixed size per item. That is what makes arrays fast.

</details>

---

# Hour 17: Calculating with whole arrays

## Learn

### Vectorising

Doing maths on a whole array in one expression is called **vectorising**. It replaces a Python loop. It is shorter, and much faster because the loop runs inside fast compiled code:

```pycon
>>> import numpy as np
>>> x = np.arange(5)
>>> x ** 2
array([ 0,  1,  4,  9, 16])
>>> x + 10
array([10, 11, 12, 13, 14])
>>> np.sqrt(x)
array([0.        , 1.        , 1.41421356, 1.73205081, 2.        ])
>>> x > 2
array([False, False, False,  True,  True])
>>> np.where(x > 2, "big", "small")
array(['small', 'small', 'small', 'big', 'big'], dtype='<U5')
>>> np.clip(x * 100, 0, 255)
array([  0, 100, 200, 255, 255])
```

- `np.where(condition, a, b)` picks `a` where the condition is true and `b` otherwise.
- `np.clip(x, low, high)` forces every value into the range. You will need it for images.

### Totals

`sum`, `mean`, `min`, `max` work on the whole array. For a 2D array, `axis` says along which direction to combine: `axis=0` goes **down the rows** (one answer per column), `axis=1` goes **across the columns** (one answer per row):

```pycon
>>> import numpy as np
>>> m = np.array([[1, 2, 3], [4, 5, 6]])
>>> m.sum()
np.int64(21)
>>> m.sum(axis=0)
array([5, 7, 9])
>>> m.sum(axis=1)
array([ 6, 15])
>>> m.mean(axis=1)
array([2., 5.])
>>> m.max()
np.int64(6)
```

### Broadcasting

What happens when two arrays have **different shapes**? NumPy lines their shapes up **from the right**. A direction of size 1 (or a missing direction) is **stretched** to match. This is called **broadcasting**.

The project uses it for zones. A zone in `config.json` has corners as **fractions** of the picture. To get pixels, multiply the x values by the width and the y values by the height. One line does it for every corner:

```pycon
>>> import numpy as np
>>> corners = np.array([[0.15, 0.25], [0.85, 0.25], [0.85, 0.95]])
>>> corners.shape
(3, 2)
>>> size = np.array([810, 1080])
>>> size.shape
(2,)
>>> corners * size
array([[ 121.5,  270. ],
       [ 688.5,  270. ],
       [ 688.5, 1026. ]])
```

`corners` has shape `(3, 2)` and `size` has shape `(2,)`. Aligned from the right, `2` matches `2`, so `size` is stretched down all 3 rows: every x is multiplied by `810`, every y by `1080`.

## Lab 6.2: Speed race

Create `exercises/day06/speed_test.py`. It squares one million numbers with a list comprehension and with NumPy, and measures both with `time.perf_counter()` (a precise stopwatch).

**`exercises/day06/speed_test.py`**

```python
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
```

```text
$ python exercises/day06/speed_test.py
Python list: 9.9 ms
NumPy array: 0.7 ms
NumPy is about 14 times faster
```

Your numbers will be different: it depends on your computer. NumPy should be many times faster. Run it twice to see that the result changes a little each time.

## Lab 6.3: Broadcasting practice

1. Make `prices = np.array([10, 20, 30])` and add a tax of 10% to every price in one line.
2. Make a `(3, 3)` array of zeros, then add `np.array([1, 2, 3])` to it. What do you get? Why?
3. Given `size = np.array([1280, 720])` and the corner `np.array([0.5, 0.5])`, find the centre of a 1280 x 720 picture in pixels.

<details><summary>Answers</summary>

```pycon
>>> import numpy as np
>>> prices = np.array([10, 20, 30])
>>> prices * 1.10
array([11., 22., 33.])
>>> np.zeros((3, 3)) + np.array([1, 2, 3])
array([[1., 2., 3.],
       [1., 2., 3.],
       [1., 2., 3.]])
>>> np.array([0.5, 0.5]) * np.array([1280, 720])
array([640., 360.])
```

For 2: the shape `(3,)` is stretched down the 3 rows, so each row becomes `[1, 2, 3]`.

</details>

## Check yourself

1. What is vectorising and why is it faster than a loop?
2. For `m = np.array([[1, 2], [3, 4]])`, what are `m.sum(axis=0)` and `m.sum(axis=1)`?
3. Can you multiply a `(3, 2)` array by a `(2,)` array? What about by a `(3,)` array?

<details><summary>Answers</summary>

1. Doing the maths on the whole array in one expression. The loop runs in fast compiled code instead of in slow Python code.
2. `[4, 6]` (column sums) and `[3, 7]` (row sums).
3. `(2,)`: yes, it is stretched across the 3 rows. `(3,)`: no. Aligned from the right, `3` does not match `2`, so NumPy raises an error.

</details>

---

# Hour 18: A picture is an array

## Learn

A digital picture is a grid of **pixels**. Each pixel has three numbers, the amounts of **blue, green and red** (in that order in OpenCV, **BGR**), each from 0 (none) to 255 (full). A colour picture is therefore an array with shape `(height, width, 3)` and type `uint8` ("unsigned 8-bit integer": a whole number from 0 to 255).

```text
image.shape = (height, width, 3)
image[row, column]      -> [blue, green, red]
image[y1:y2, x1:x2]     -> a rectangle (crop), rows first!
```

**Rows come first.** In maths you say `(x, y)`, but in an array the first index is the row, which is **y**. So a crop with a box `(x1, y1, x2, y2)` is `image[y1:y2, x1:x2]`.

OpenCV reads a picture with `cv2.imread`. For practice we use a photo that comes with the `ultralytics` package (the YOLO library): `ASSETS / "bus.jpg"`. (The first import can take a few seconds.)

## Lab 6.4: Read, crop and flip

Create `exercises/day06/image_basics.py`. It prints the shape and type, reads one pixel, crops one person using a box, and flips the picture two ways. It saves the results in an `output` folder.

**`exercises/day06/image_basics.py`**

```python
from pathlib import Path

import cv2
from ultralytics.utils import ASSETS

image = cv2.imread(str(ASSETS / "bus.jpg"))
print("shape:", image.shape)  # (height, width, channels)
print("data type:", image.dtype)
height, width, channels = image.shape
print(f"{width} x {height} pixels, {channels} colour channels")
print("pixel at row 300, column 400 (B, G, R):", image[300, 400])

# Crop one person with a box (x1, y1, x2, y2) in pixels. Rows come first: image[y1:y2, x1:x2]
x1, y1, x2, y2 = 47, 400, 239, 904
person = image[y1:y2, x1:x2]
print("crop shape:", person.shape)

mirror = image[:, ::-1]  # every row, columns in reverse order
rgb = image[..., ::-1]  # reverse the colour channels: BGR -> RGB
print("mirror shape:", mirror.shape)
print("same pixel as (R, G, B):", rgb[300, 400])

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/day06_person.jpg", person)
cv2.imwrite("output/day06_mirror.jpg", mirror)
```

```text
$ python exercises/day06/image_basics.py
shape: (1080, 810, 3)
data type: uint8
810 x 1080 pixels, 3 colour channels
pixel at row 300, column 400 (B, G, R): [235 235 235]
crop shape: (504, 192, 3)
mirror shape: (1080, 810, 3)
same pixel as (R, G, B): [235 235 235]
```

Open `output/day06_person.jpg`. You cut one person out of the photo with a single line of slicing:

![The person cropped from the photo](images/day06-person.jpg)

Notes:

- `image[:, ::-1]` means "all rows; columns from the end to the start". It mirrors the picture.
- `image[..., ::-1]` reverses the **last** direction, the three colour numbers. It turns BGR into RGB. (Matplotlib and most other libraries expect RGB. OpenCV expects BGR. This difference causes strange blue skin colours if you forget it.)
- `Path("output").mkdir(exist_ok=True)` creates the folder if it is missing.

## Lab 6.5: The brightness bug

Let us make the picture brighter by adding 60 to every pixel. Easy? Look at what happens. The type `uint8` can only hold 0 to 255, and when a number goes past 255 it **wraps around** to the start:

```pycon
>>> import numpy as np
>>> pixel = np.array([200, 250], dtype=np.uint8)
>>> pixel + 60
array([ 4, 54], dtype=uint8)
>>> pixel.astype(np.int16) + 60
array([260, 310], dtype=int16)
>>> np.clip(pixel.astype(np.int16) + 60, 0, 255).astype(np.uint8)
array([255, 255], dtype=uint8)
```

`250 + 60 = 310`, but a `uint8` shows `310 - 256 = 54`. A white pixel would become nearly black! The correct way: switch to a bigger type (`int16`), add, **clip** back into 0 to 255, and convert back to `uint8`.

Create `exercises/day06/brighten.py` and compare the wrong and the right way on the whole picture:

**`exercises/day06/brighten.py`**

```python
from pathlib import Path

import cv2
import numpy as np
from ultralytics.utils import ASSETS

image = cv2.imread(str(ASSETS / "bus.jpg"))

wrong = image + 60  # uint8 wraps around: 235 + 60 becomes 39
right = np.clip(image.astype(np.int16) + 60, 0, 255).astype(np.uint8)

print("original pixel :", image[300, 400])
print("wrong (wrapped):", wrong[300, 400])
print("right (clipped):", right[300, 400])

# Put the three pictures side by side (shrink them first so the result is small)
small = [cv2.resize(p, (270, 360)) for p in (image, wrong, right)]
summary = np.hstack(small)

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/day06_summary.jpg", summary)
print("saved output/day06_summary.jpg", summary.shape)
```

```text
$ python exercises/day06/brighten.py
original pixel : [235 235 235]
wrong (wrapped): [39 39 39]
right (clipped): [255 255 255]
saved output/day06_summary.jpg (360, 810, 3)
```

Open `output/day06_summary.jpg`. From the left: the original, the wrong version (bright areas turned dark and strange), and the correct version.

![Original, wrapped-around (wrong) and clipped (right) brightness](images/day06-summary.jpg)

You will meet this bug again when you add or subtract images (for example in motion detection on Day 8). OpenCV has safe functions for it (`cv2.add`, `cv2.absdiff`), and you will use them.

## Lab 6.6: A zone in pixels

Connect it to the project. `config.json` has a zone with corners as fractions. Turn them into pixel positions for the `bus.jpg` picture (810 pixels wide, 1080 high).

**`exercises/day06/polygon_numpy.py`**

```python
import json

import numpy as np

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

width, height = 810, 1080  # the size of bus.jpg
zone = cfg["zones"][0]

# The corners in config.json are fractions from 0 to 1. Multiply by the picture size.
polygon = np.array(zone["polygon"], dtype=np.float32) * np.array([width, height], dtype=np.float32)

print(zone["name"], "corners in pixels:")
print(polygon)
print("as whole numbers, ready to draw:")
print(polygon.astype("int32"))
```

```text
$ python exercises/day06/polygon_numpy.py
front_door corners in pixels:
[[ 121.50001  270.     ]
 [ 688.5      270.     ]
 [ 688.5     1026.     ]
 [ 121.50001 1026.     ]]
as whole numbers, ready to draw:
[[ 121  270]
 [ 688  270]
 [ 688 1026]
 [ 121 1026]]
```

- `dtype=np.float32` is the type OpenCV expects for polygon points. A `float32` keeps about 7 digits, so `121.5` can print as `121.50001`. That is normal and harmless here.
- `.astype("int32")` drops the decimals. Drawing functions want whole pixels.

Tomorrow this becomes a method of the `RuleEngine` that the drawing code uses.

## Check yourself (exit ticket)

1. What is the shape of a 720 x 1280 colour picture (720 high, 1280 wide)?
2. Which slice crops the box `(x1, y1, x2, y2)` from `image`?
3. What is the value of a `uint8` `250 + 60`? How do you avoid the problem?
4. What does `image[:, ::-1]` do?
5. OpenCV colours are in which order?

<details><summary>Answers</summary>

1. `(720, 1280, 3)`.
2. `image[y1:y2, x1:x2]`. Rows (y) come first.
3. `54` (it wraps around). Convert to a bigger type, calculate, `np.clip(..., 0, 255)`, and convert back; or use `cv2.add`.
4. It mirrors the picture left to right (all rows, columns in reverse).
5. Blue, green, red (BGR).

</details>

## Homework (optional, 20 minutes)

Write `exercises/day06/darken_half.py`: read the picture, make the **right half** of it 50% darker (multiply by 0.5), and save it. Hint: the right half is `image[:, width // 2:]`. Watch the type after the multiplication (`astype(np.uint8)`).

---

# Day 6 wrap-up

## Checklist

- [ ] You can read `shape`, `dtype` and `size` of an array and explain them.
- [ ] `image_basics.py` and `brighten.py` run and create files in `output/`.
- [ ] You can explain why `image + 60` is wrong and what to do instead.
- [ ] `polygon_numpy.py` prints the zone in pixels.
- [ ] You committed your work: `git add .` then `git commit -m "Day 6: numpy exercises"`.

## Your project folder today

```text
my-intelligence-system/
├── (everything from Day 5)
├── output/                      <- created by your scripts (ignored by git)
│   ├── day06_person.jpg
│   ├── day06_mirror.jpg
│   └── day06_summary.jpg
└── exercises/
    └── day06/
        ├── speed_test.py
        ├── image_basics.py
        ├── brighten.py
        └── polygon_numpy.py
```

Solutions are in [`solutions/day06/`](solutions/day06/).

## Instructor notes

- **Shape thinking** is the hardest idea of the day. Draw a 2D array on the board and write `shape (2, 3)` next to it, then add a third direction for colours.
- **Rows come first.** Most students will write `image[x, y]` once. Make them predict the shape of a crop before running it.
- **Show the bug on purpose.** Hour 18's wrapped-around brightness is memorable. Let students look at the wrong picture before you explain it.
- **BGR vs RGB:** show a picture with the colours swapped (`image[..., ::-1]` shown with matplotlib) so students remember it.
- **Speed race:** if a student's NumPy time prints as `0.0 ms`, ask them to run with a bigger `size`. Make sure nobody leaves thinking "NumPy is faster because it is magic": it is faster because the loop runs in compiled code.
- **If you are behind:** skip Lab 6.3 and the homework. Labs 6.4 and 6.5 are the foundation for Day 7.
- **Fast finishers:** convert the picture to grey by averaging the three channels (`image.mean(axis=2).astype(np.uint8)`) and compare it with what `cv2.cvtColor` gives on Day 7.

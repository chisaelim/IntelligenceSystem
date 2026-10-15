# Day 1: Setup and first programs

**Hours 1-3 of 45** · Python level needed: none · Project milestone: none yet (today you get your tools ready)

## What you can do at the end of today

- Explain what Python, conda and an environment are.
- Open a terminal, activate `python-course`, and check that every package works.
- Run a Python file from VS Code and from the terminal, and run a notebook in JupyterLab.
- Read an error message and find the line that caused it.
- Use variables, numbers, text, f-strings, `print()` and `input()`.

## Where today fits in the project

In 45 hours you will build an **Intelligence System**: a webcam that watches a place, recognises people, remembers what it saw, decides what matters and sends a photo alert to your phone through Telegram.

```text
webcam -> YOLO detection + tracking -> rules (night? zone? unusual hour?) -> SQLite memory -> Telegram photo
```

You do not need to understand any of this yet. Every day adds one small piece. Today you only prepare the tools and write your first lines of Python.

| Week | Days | You learn | You build |
|---|---|---|---|
| 1 | 1-5 | Python basics: decisions, loops, functions, lists, files, classes | settings loader, data classes, night rule |
| 2 | 6-10 | NumPy, images and video (OpenCV), SQL, HTTP and Telegram | drawing, camera loop, event memory |
| 3 | 11-15 | Threads, YOLO, tracking, rules, putting it all together | alerts, detector, rules, the final system |

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 1 | 10 | Instructor demo of the finished system and the 15-day map |
| | 15 | Talk: Python, Anaconda, conda, environments |
| | 25 | **Lab 1.1** Check your environment |
| | 10 | Wrap-up and help for anyone whose install is not finished |
| 2 | 10 | Terminal basics |
| | 10 | VS Code: open a folder, choose the interpreter |
| | 10 | Run a script, run a notebook |
| | 10 | Reading error messages |
| | 20 | **Lab 1.2** Hello world, two ways, and break it on purpose |
| 3 | 15 | Talk: variables, numbers, text, f-strings, `input()` |
| | 10 | Live demo in the Python console |
| | 25 | **Labs 1.3-1.5** Greeting, temperature, frame size |
| | 10 | Review and exit ticket |

> **Instructor, before class:** have the finished project ready to show. Run `python security_camera.py --dry-run` from the course folder, walk in front of the camera, and show the preview window with the boxes. If you can, also show a real Telegram alert on a phone. Do not explain how it works. Say: "At the end of Day 15 each of you will show me your own version."

---

# Hour 1: What are Python, conda and an environment?

## Learn

**Python** is a programming language. You write instructions in a text file. The Python *interpreter* reads the file from top to bottom and does what it says. Python is popular for AI because it is easy to read and has many free libraries (NumPy, OpenCV, PyTorch) that do the hard work for you.

**Anaconda** is a free download with Python, a package manager called **conda**, and many tools (like JupyterLab). **conda** can install libraries and can create *environments*.

**An environment** is a folder with its own copy of Python and its own libraries. Think of one toolbox per project. Project A can use one version of a library and project B another, and they never break each other.

For this course you use one environment called **`python-course`**. It already contains everything you need:

| Package | What we use it for | Day |
|---|---|---|
| Python 3.11 | the language | 1 |
| JupyterLab | notebooks for trying ideas | 1 |
| NumPy | fast arrays, images are arrays | 6 |
| OpenCV (`cv2`) | read the camera, draw on images | 7-8 |
| pandas, matplotlib | tables and charts | 9 |
| requests | talk to Telegram over the internet | 10 |
| PyTorch + ultralytics | YOLO object detection and tracking | 12-13 |

The environment is a big download (about 3 to 5 GB). If yours is not installed yet, start the install now (see Lab 1.1 step 2) and keep going with the lesson while it downloads.

## The terminal

Conda commands run in a **terminal**:

| System | How to open it |
|---|---|
| Windows | Start menu, type **Anaconda Prompt**, open it. Use this one, not the normal Command Prompt. |
| macOS | Press Cmd+Space, type **Terminal**, press Enter. |
| Linux | Open your terminal application. |

If you see `conda: command not found` on macOS or Linux, close the terminal and open a new one. If it still fails, ask the instructor to run `conda init` with you.

The five conda commands you need today:

| Command | What it does |
|---|---|
| `conda --version` | shows that conda works |
| `conda env list` | lists your environments (`*` marks the active one) |
| `conda activate python-course` | switches to the course environment |
| `python --version` | shows the Python version of the active environment |
| `conda deactivate` | leaves the environment |

When an environment is active, its name appears at the start of the line, like `(python-course) $`. If you do not see it, you are not inside the environment and `import cv2` will fail.

## Lab 1.1: Check your environment

1. Open the terminal and run `conda --version`. You should see a version number.
2. Run `conda env list`. Look for `python-course`.
   - **If it is missing**, go to the course folder and create it. Use the file for your system:
     ```bash
     conda env create -f environment-windows.yml    # Windows
     conda env create -f environment-macos.yml      # macOS (Apple chip)
     conda env create -f environment-linux.yml      # Linux
     ```
     This takes a long time. Leave it running and continue to Hour 2 in a **second** terminal window.
3. Activate it: `conda activate python-course`. The prompt now starts with `(python-course)`.
4. Run `python --version`. You should see `Python 3.11.something`.
5. Create a folder for your work and go into it:
   ```bash
   mkdir my-intelligence-system
   cd my-intelligence-system
   mkdir exercises
   mkdir exercises/day01
   ```
6. Create the file `exercises/day01/check_env.py` with the code below (use VS Code in Hour 2 if you do not have it yet, or any text editor for now), then run it.

**`exercises/day01/check_env.py`**

```python
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
```

```bash
python exercises/day01/check_env.py
```

You should see something like this. Version numbers can be a little different on your computer, and the GPU line may say `False` (that is fine, the CPU works too):

```text
$ python exercises/day01/check_env.py
Python: 3.11.17
numpy: 2.1.3
opencv: 4.12.0
torch: 2.10.0
ultralytics: 8.4.177
requests: 2.34.2
pandas: 2.2.3
GPU available: True
Everything is installed. You are ready!
```

### If something goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `conda: command not found` | the terminal does not know conda | open a new terminal; on Windows use Anaconda Prompt |
| `Could not find conda environment: python-course` | the environment is not created yet | run the `conda env create` command from step 2 |
| `ModuleNotFoundError: No module named 'cv2'` | you are not inside `python-course` | run `conda activate python-course` and try again |
| `Creating new Ultralytics Settings` on the first run | normal, it only happens once | ignore it |
| `CondaToSNonInteractiveError` (Windows) | conda wants you to accept its terms of service | run the `conda tos accept ...` command it prints, then try again |
| The download is very slow or stops | the network is busy | keep the terminal open, ask the instructor, or continue on a classmate's screen for today |

## Check yourself

1. What is the difference between conda and an environment?
2. How can you tell that `python-course` is active?
3. Why do we use one environment for the whole course?

<details><summary>Answers</summary>

1. conda is the tool (it installs packages and manages environments). An environment is one folder with its own Python and packages that conda created.
2. The prompt starts with `(python-course)`.
3. So every student has the same Python and the same library versions, and the programs behave the same on every computer.

</details>

---

# Hour 2: Terminal, VS Code, scripts, notebooks and errors

## Terminal basics

You will type commands all week, so learn these. The commands differ a little between systems:

| Task | macOS / Linux | Windows (Anaconda Prompt) |
|---|---|---|
| Where am I? | `pwd` | `cd` |
| List the files here | `ls` | `dir` |
| Make a folder | `mkdir name` | `mkdir name` |
| Go into a folder | `cd name` | `cd name` |
| Go up one folder | `cd ..` | `cd ..` |
| Clear the screen | `clear` | `cls` |

Four tricks that save time:

- Press **Tab** to finish a file or folder name.
- Press **Up arrow** to bring back the last command.
- Press **Ctrl+C** to stop a program that is running.
- If a path has a space in it, put it in quotes: `cd "My Folder"`.

## VS Code

VS Code is a free code editor. It colours your code, shows errors, and has a terminal inside.

1. Install it from `code.visualstudio.com`.
2. Open VS Code, click the Extensions icon (four squares), search for **Python** (by Microsoft) and install it.
3. Choose **File > Open Folder** and open your `my-intelligence-system` folder.
4. Choose the interpreter. Press Ctrl+Shift+P (Cmd+Shift+P on macOS), type **Python: Select Interpreter**, and pick the one named `python-course`. It looks like `.../envs/python-course/bin/python` (macOS/Linux) or `...\envs\python-course\python.exe` (Windows).
5. Open the built-in terminal with **Terminal > New Terminal**. The prompt should show `(python-course)`. If it does not, type `conda activate python-course`.

If VS Code does not list `python-course`, press Ctrl+Shift+P, run **Developer: Reload Window**, and look again.

## Run a script, run a notebook

A **script** is a text file that ends with `.py`. You run it from the terminal: `python exercises/day01/hello.py`. In VS Code you can also click the **Run Python File** button (a triangle at the top right).

A **notebook** (`.ipynb`) is a page made of cells. You run one cell at a time and see the result under it. Start JupyterLab from your project folder, inside the environment:

```bash
jupyter lab
```

A browser tab opens. Choose **Python 3** under Notebook. Type code in a cell and press **Shift+Enter** to run it. The value of the last line of a cell is shown under the cell.

| | Script (`.py`) | Notebook (`.ipynb`) |
|---|---|---|
| Good for | the real program, anything that must run by itself | trying ideas, charts, learning |
| Runs | all at once, from the terminal | one cell at a time |
| Our camera program | **yes**, it must run alone for hours | no |

## Reading error messages

Every beginner sees errors every day. They are not bad news. An error message tells you **what** went wrong and **where**. Read it from the **bottom**:

```pycon
>>> print("Hello)
  File "<stdin>", line 1
    print("Hello)
          ^
SyntaxError: unterminated string literal (detected at line 1)
>>> camera = 5
>>> print(camra)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'camra' is not defined
>>> "fps: " + 30
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can only concatenate str (not "int") to str
>>> 10 / 0
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ZeroDivisionError: division by zero
>>> import cv3
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'cv3'
```

How to read a traceback:

1. **The last line** says the error type and the reason (`NameError: name 'camra' is not defined`).
2. **The lines above** say which file and which line number. In a script you see `File "...py", line 7`.
3. Go to that line and look for typos, missing quotes or brackets, and wrong types.

| Error | Usual cause |
|---|---|
| `SyntaxError` | missing quote, bracket or colon |
| `NameError` | a typo in a name, or using a variable before you created it |
| `TypeError` | mixing types, for example text + number |
| `ZeroDivisionError` | dividing by zero |
| `ModuleNotFoundError` | a typo in the package name, or you are not in the right environment |
| `IndentationError` | the spaces at the start of a line are wrong |

## Lab 1.2: Hello world, two ways, and break it on purpose

**Part A: a script.** In VS Code create `exercises/day01/hello.py`:

**`exercises/day01/hello.py`**

```python
print("Hello, Intelligence System!")
```

Run it in the terminal:

```text
$ python exercises/day01/hello.py
Hello, Intelligence System!
```

Then run it again with the **Run Python File** button.

**Part B: a notebook.** In JupyterLab create a notebook named `hello.ipynb` in `exercises/day01`. In the first cell type `print("Hello from a notebook")` and press Shift+Enter. In a second cell type `2 + 3 * 4` and run it. Notice that the second cell shows the answer without `print`.

**Part C: break it on purpose.** Open the Python console by typing `python` in the terminal (type `exit()` to leave it). Type each line below, read the error, then fix it:

| Type this | Read the error | Fix |
|---|---|---|
| `print("hi)` | `SyntaxError: unterminated string literal` | add the closing quote |
| `Print("hi")` | `NameError: name 'Print' is not defined` | Python is case sensitive: `print` |
| `"age: " + 25` | `TypeError` | convert the number: `"age: " + str(25)` |
| `import numpyy` | `ModuleNotFoundError` | fix the spelling: `numpy` |

## Check yourself

1. In a traceback, which line do you read first?
2. Why is the camera program a script and not a notebook?

<details><summary>Answers</summary>

1. The last line. It says the type of error and why it happened.
2. A script runs by itself from the terminal, for as long as we want. A notebook needs a person to run each cell.

</details>

---

# Hour 3: Variables, numbers, text and input

## Learn

A **variable** is a name for a value. You create it with `=`:

```pycon
>>> camera_name = "Front door"
>>> fps = 30
>>> confidence = 0.87
>>> is_night = False
>>> print(camera_name, fps, confidence, is_night)
Front door 30 0.87 False
>>> type(camera_name)
<class 'str'>
>>> type(fps)
<class 'int'>
>>> type(confidence)
<class 'float'>
>>> type(is_night)
<class 'bool'>
```

The four basic types:

| Type | Meaning | Example |
|---|---|---|
| `int` | whole number | `30` |
| `float` | number with a decimal point | `0.87` |
| `str` | text (string) | `"Front door"` |
| `bool` | `True` or `False` | `False` |

**Naming rules.** Use letters, digits and `_`. A name cannot start with a digit. Capital letters matter (`fps` and `FPS` are different). Use `snake_case` for variables (`camera_name`). Use `UPPER_CASE` for numbers that never change (`MAX_ATTEMPTS`). Do not name a variable `print`, `input`, `type` or `list`, because you hide the real tool.

**Maths.** `+ - * /` work as you expect. Three more are very useful:

```pycon
>>> 7 / 2
3.5
>>> 7 // 2
3
>>> 7 % 2
1
>>> 2 ** 10
1024
>>> 10 + 4 * 2
18
>>> (10 + 4) * 2
28
>>> round(3.14159, 2)
3.14
```

`/` always gives a float. `//` is division that drops the decimals. `%` is the remainder (we will use it on Day 2 to do something "every 30th frame").

**Text.** Text goes in quotes. You can join it, repeat it and change it:

```pycon
>>> "cam" + "era"
'camera'
>>> "ab" * 3
'ababab'
>>> len("person")
6
>>> "person".upper()
'PERSON'
>>> "  front door  ".strip()
'front door'
>>> "front door".replace("door", "gate")
'front gate'
>>> "Front Door".lower()
'front door'
```

**f-strings** put values inside text. Write `f` before the quote and put names in `{}`. After a colon you can control the format:

```pycon
>>> label = "person"
>>> confidence = 0.87345
>>> f"I see a {label} ({confidence:.2f})"
'I see a person (0.87)'
>>> f"{1280 * 720:,} pixels"
'921,600 pixels'
>>> f"{confidence:.0%}"
'87%'
```

`:.2f` means "two digits after the decimal point". `:,` adds thousands separators. `:.0%` shows a percentage. You will use f-strings in almost every program, including the final project.

**Input.** `input("question")` asks the user to type something and gives back **text**, even if the user types a number. Convert it with `int()` or `float()`:

```pycon
>>> int("42") + 1
43
>>> float("0.5") * 2
1.0
>>> "4" + "2"
'42'
>>> int("abc")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: invalid literal for int() with base 10: 'abc'
```

## Lab 1.3: Greeting

Create `exercises/day01/greeting.py`. Ask for a name and a city, then print one sentence with both.

**`exercises/day01/greeting.py`**

```python
name = input("What is your name? ")
city = input("Which city do you live in? ")
print(f"Hello, {name}! Welcome to the Intelligence System course in {city}.")
```

```text
$ python exercises/day01/greeting.py
What is your name? Sokha
Which city do you live in? Phnom Penh
Hello, Sokha! Welcome to the Intelligence System course in Phnom Penh.
```

## Lab 1.4: Temperature converter

The formula is `F = C * 9 / 5 + 32`. Remember that `input()` gives text, so convert it to a `float` first.

**`exercises/day01/temperature.py`**

```python
celsius = float(input("Temperature in Celsius: "))
fahrenheit = celsius * 9 / 5 + 32
print(f"{celsius:.1f} C = {fahrenheit:.1f} F")
```

```text
$ python exercises/day01/temperature.py
Temperature in Celsius: 36.6
36.6 C = 97.9 F
```

## Lab 1.5: How big is a video?

This lab connects to the project. A camera frame is a grid of pixels. Each pixel has three numbers (blue, green, red) and each number takes one byte. How much memory does video need?

**`exercises/day01/frame_size.py`**

```python
width = int(input("Frame width in pixels: "))
height = int(input("Frame height in pixels: "))
fps = int(input("Frames per second: "))

pixels = width * height
bytes_per_frame = pixels * 3  # 3 colour values (blue, green, red), 1 byte each
mb_per_frame = bytes_per_frame / 1024 / 1024
mb_per_second = mb_per_frame * fps
gb_per_hour = mb_per_second * 3600 / 1024

print(f"One frame has {pixels:,} pixels")
print(f"One frame needs {mb_per_frame:.2f} MB")
print(f"One second of video needs {mb_per_second:.1f} MB")
print(f"One hour of video needs {gb_per_hour:.0f} GB (before compression)")
```

```text
$ python exercises/day01/frame_size.py
Frame width in pixels: 1280
Frame height in pixels: 720
Frames per second: 30
One frame has 921,600 pixels
One frame needs 2.64 MB
One second of video needs 79.1 MB
One hour of video needs 278 GB (before compression)
```

Look at the last line: one hour of plain video is hundreds of gigabytes. This is why our security camera does **not** save everything. It saves a snapshot only when something important happens.

**Try these:** run it for Full HD (`1920`, `1080`, `30`) and for a small `640` by `480` camera at `15` frames per second. How do the numbers change?

## Check yourself (exit ticket)

1. What type is `"42"`? What type is `42`? What is `"42" + "1"`?
2. What does `7 // 2` give? What does `7 % 2` give?
3. Write an f-string that prints `Camera front door runs at 30 fps` using the variables `name` and `fps`.
4. `age = input("Age: ")` and the user types `20`. What does `age + 1` do? How do you fix it?
5. Why does `print(Hello)` fail but `print("Hello")` work?

<details><summary>Answers</summary>

1. `"42"` is `str`, `42` is `int`, and `"42" + "1"` is `"421"` (text is joined, not added).
2. `3` and `1`.
3. `f"Camera {name} runs at {fps} fps"`.
4. `age` is the text `"20"`, so `age + 1` raises a `TypeError`. Fix: `age = int(input("Age: "))`.
5. Without quotes Python thinks `Hello` is a variable name. With quotes it is text.

</details>

## Homework (optional, 15 minutes)

Write `exercises/day01/birth_year.py`. Ask for a name, an age and the current year, and print the year the person was born.

<details><summary>Solution</summary>

**`exercises/day01/birth_year.py`**

```python
name = input("Your name: ")
age = int(input("Your age: "))
this_year = int(input("What year is it now? "))

birth_year = this_year - age
print(f"{name}, you were born around {birth_year}.")
```

```text
$ python exercises/day01/birth_year.py
Your name: Dara
Your age: 20
What year is it now? 2026
Dara, you were born around 2006.
```

</details>

---

# Day 1 wrap-up

## Checklist

- [ ] `conda activate python-course` works and the prompt shows `(python-course)`.
- [ ] `check_env.py` runs and prints "Everything is installed".
- [ ] VS Code uses the `python-course` interpreter and you can run a file from it.
- [ ] You ran a notebook cell in JupyterLab.
- [ ] `greeting.py`, `temperature.py` and `frame_size.py` work.

## Today you built

```text
my-intelligence-system/
└── exercises/
    └── day01/
        ├── check_env.py
        ├── hello.py
        ├── greeting.py
        ├── temperature.py
        ├── frame_size.py
        └── hello.ipynb
```

Solutions for every file are in [`solutions/day01/`](solutions/day01/).

## Instructor notes

- **The install is the risk.** Check at the start of hour 1 who has the environment. Anyone who does not should start `conda env create` right away and follow the lesson on another screen. Do not wait for them.
- **Common problems:** Windows students opening the normal Command Prompt instead of Anaconda Prompt; macOS students who need `conda init`; VS Code not showing the interpreter (reload the window); students who run `python` while the prompt shows `(base)` instead of `(python-course)`.
- **Pace:** Hour 3 is the first real Python. Let students type every line themselves; do not paste. Aim for everyone to have seen at least one `TypeError` from `input()` today.
- **Fast finishers:** make the temperature converter go both ways, or compute how many minutes of video fit on a 64 GB card at 1280x720 and 30 fps (uncompressed).
- **Do not teach yet:** loops, functions, lists. They come on Days 2 and 3.

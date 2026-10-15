# Day 4: Files, errors and modules

**Hours 10-12 of 45** · **Milestone 1:** the settings and secrets loader (`intelligence/config.py`)

## What you can do at the end of today

- Read and write text files with `with open(...)` and with `pathlib`.
- Parse a `KEY=VALUE` file (the `.env` file that will keep your Telegram token).
- Handle errors with `try` / `except` and print friendly messages.
- Find a bug with print statements and with the VS Code debugger.
- Split code into **modules** and a **package**, and import between them.
- Start your real project: the `intelligence/` package with `config.py`.

## Where today fits in the project

From today you build the real project, not only exercises. The finished program must know its settings (`config.json`) and its secrets (the Telegram token and chat id). Secrets must **never** be written inside the code or committed to git, so they live in a separate file called `.env`. Today you write the code that reads both files and the package structure the rest of the project grows into.

```text
my-intelligence-system/
├── .env                    <- your secrets (never share, never commit)
├── .env.example            <- the same file with fake values (safe to share)
├── config.json             <- settings
├── security_camera.py      <- the program you start
├── intelligence/           <- the package: all the real code
│   ├── __init__.py
│   └── config.py           <- today
├── tests/                  <- small self-checks
└── exercises/              <- practice files from each day
```

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 10 | 5 | Warm-up: Day 3 homework discussion |
| | 20 | Talk: files, text methods, paths, `.env` |
| | 10 | Live demo |
| | 25 | **Lab 4.1** Parse a `.env` file |
| 11 | 20 | Talk: exceptions and debugging |
| | 10 | Live demo of the VS Code debugger |
| | 30 | **Labs 4.2-4.3** Safe loading, find the bug |
| 12 | 20 | Talk: modules, packages, `if __name__ == "__main__"` |
| | 10 | Live demo |
| | 30 | **Lab 4.4 (Milestone 1)** The `intelligence` package |

---

# Hour 10: Files, paths and the `.env` file

## Learn

### Reading and writing text files

`open()` gives you a file. Always use it with **`with`** and always give `encoding="utf-8"`. The `with` block closes the file for you, even if an error happens:

```pycon
>>> from pathlib import Path
>>> note = Path("note.txt")
>>> note.write_text("line one\nline two\n", encoding="utf-8")
18
>>> note.exists()
True
>>> note.read_text(encoding="utf-8")
'line one\nline two\n'
>>> with open("note.txt", encoding="utf-8") as f:
...     for line in f:
...         print(line.strip())
...
line one
line two
>>> with open("note.txt", "a", encoding="utf-8") as f:
...     f.write("line three\n")
...
11
>>> note.read_text(encoding="utf-8").splitlines()
['line one', 'line two', 'line three']
```

| Mode | Meaning |
|---|---|
| `"r"` (default) | read |
| `"w"` | write. **It erases the old content first!** |
| `"a"` | append to the end |

`\n` is the "new line" character. `.splitlines()` cuts a text into a list of lines.

### Text methods for parsing

To read `KEY=VALUE` lines you need a few text methods:

```pycon
>>> line = '  TELEGRAM_CHAT_ID = "12345"  '
>>> line = line.strip()
>>> line
'TELEGRAM_CHAT_ID = "12345"'
>>> "a=b=c".split("=")
['a', 'b', 'c']
>>> "a=b=c".split("=", 1)
['a', 'b=c']
>>> key, value = line.split("=", 1)
>>> key.strip()
'TELEGRAM_CHAT_ID'
>>> value.strip().strip('"')
'12345'
>>> "# a comment".startswith("#")
True
```

`split("=", 1)` splits only at the **first** `=`. This matters because a token can itself contain special characters.

### Paths with `pathlib`

A path is the address of a file. Writing paths as plain text is fragile: Windows uses `C:\Users\Sokha\...` (backslashes) and macOS/Linux use `/Users/sokha/...`. The `pathlib` module handles this for you. Use `/` to join pieces:

```pycon
>>> from pathlib import Path
>>> folder = Path("data")
>>> database = folder / "events.db"
>>> database
PosixPath('data/events.db')
>>> database.name
'events.db'
>>> database.suffix
'.db'
>>> database.parent
PosixPath('data')
>>> database.exists()
False
```

(On Windows `Path` shows as `WindowsPath('data/events.db')`. It is the same idea.)

Useful methods: `.exists()`, `.is_file()`, `.read_text()`, `.write_text()`, `.mkdir(parents=True, exist_ok=True)` (create a folder, no error if it already exists), `.parent`, `.name`, `.suffix`.

**Which folder is "here"?** A relative path like `config.json` starts from the **working folder**: the folder where you ran the command, not the folder of the script. If you run `python exercises/day04/parse_env.py` from `my-intelligence-system`, then `config.json` means `my-intelligence-system/config.json`. If you run from another folder, the file is not found. Later today you will learn how to make the project find its own files from anywhere.

### The `.env` file

A `.env` file is a simple text file with one `NAME=value` per line:

```text
# Telegram settings
TELEGRAM_BOT_TOKEN=123456789:abcdef
TELEGRAM_CHAT_ID=987654321
```

- A line that starts with `#` is a comment.
- Blank lines are ignored.
- The **token** works like a password. Anyone who has it can send messages as your bot.

Rules for secrets: put them in `.env`; add `.env` to `.gitignore` (Day 5); share only `.env.example` (same names, fake values).

## Lab 4.1: Parse a `.env` file

1. In your project folder create `.env.example` and copy it to `.env`:

**`.env.example`**

```text
# Copy this file to ".env" and fill in your own values. ".env" is git-ignored, never commit it.
TELEGRAM_BOT_TOKEN=123456789:replace-with-token-from-BotFather
TELEGRAM_CHAT_ID=replace-with-your-chat-id
```

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

2. For now put **fake** values in `.env`. You will use the real token and chat id on Day 10.
3. Create `exercises/day04/parse_env.py`. Write `load_env(path)`. It must: return an empty dictionary if the file does not exist; skip blank lines and comment lines; skip lines without `=`; split at the **first** `=`; strip spaces and quotes from the key and the value.
4. At the bottom, load `.env` and print the **names** of the keys and the **length** of the token. Never print the token itself.

**`exercises/day04/parse_env.py`**

```python
from pathlib import Path


def load_env(path):
    """Read KEY=VALUE lines from a .env file into a dict."""
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


env = load_env(Path(".env"))
print("keys found:", sorted(env))
print("token length:", len(env.get("TELEGRAM_BOT_TOKEN", "")))
```

```text
$ python exercises/day04/parse_env.py
keys found: ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
token length: 24
```

Notice `encoding="utf-8-sig"`. It is the same as utf-8 but it also removes an invisible mark (a "BOM") that Windows Notepad sometimes puts at the start of a file. Without it the first key could be read as `\ufeffTELEGRAM_BOT_TOKEN` and not match.

## Check yourself

1. What does `"a=b=c".split("=", 1)` return?
2. Why do we use `with open(...)`?
3. Why is the token never printed?

<details><summary>Answers</summary>

1. `['a', 'b=c']`
2. It closes the file automatically, even when an error happens inside the block.
3. A printed token appears in the terminal, in screenshots and in logs, and anyone who sees it can control your bot.

</details>

---

# Hour 11: Exceptions and debugging

## Learn

An **exception** is Python's way to say "something went wrong". If nobody handles it, the program stops and prints a traceback. Real programs expect trouble: a file is missing, the network is down, the user typed `abc` instead of a number. You handle exceptions with `try` and `except`:

```pycon
>>> try:
...     number = int("abc")
... except ValueError:
...     print("That is not a number")
...
That is not a number
>>> try:
...     open("missing.txt")
... except FileNotFoundError as error:
...     print("Problem:", error)
...
Problem: [Errno 2] No such file or directory: 'missing.txt'
>>> def safe_divide(a, b):
...     try:
...         return a / b
...     except ZeroDivisionError:
...         return None
...
>>> safe_divide(10, 2)
5.0
>>> safe_divide(1, 0)
```

The full form:

```python
try:
    ...            # code that might fail
except SomeError:
    ...            # what to do if it fails
else:
    ...            # (optional) runs only if nothing failed
finally:
    ...            # (optional) ALWAYS runs, for cleanup
```

- **Catch specific errors** (`FileNotFoundError`, `ValueError`). A bare `except:` hides every problem, including your own typos.
- `finally` always runs. The final project uses it to release the camera even when the program crashes.
- `raise SystemExit("message")` stops the program and prints a friendly message instead of a traceback. The project uses it for fatal problems like "cannot open the camera".

```pycon
>>> def stop_with_message():
...     try:
...         print("working...")
...         raise ValueError("something broke")
...     except ValueError as error:
...         print("caught:", error)
...     finally:
...         print("cleanup always runs")
...
>>> stop_with_message()
working...
caught: something broke
cleanup always runs
```

## Debugging

When a program gives a wrong answer without an error, you must find out what happens inside. Two tools:

**1. Print debugging.** Add `print(...)` lines to see values: `print("total =", total, "count =", count)`. Simple and always available. Remove them when you are done.

**2. The VS Code debugger.** It lets you pause the program on a line and look at every variable.

1. Open the file. Click in the grey margin **left of a line number**. A red dot appears: that is a **breakpoint**.
2. Press **F5** (choose *Python File*). The program runs and **stops** at the breakpoint.
3. Look at the **Variables** panel on the left. It shows the current value of every variable.
4. Press **F10** to run one line and stop again (step over). Press **F11** to step *into* a function. Press **F5** to continue to the next breakpoint. Press **Shift+F5** to stop.

## Lab 4.2: Safe config loading

A missing or broken config file should give a clear message, not a long traceback. Write `exercises/day04/safe_load.py`. It takes an optional file name on the command line (`sys.argv[1]`; `sys.argv` is the list of words typed after `python script.py`).

**`exercises/day04/safe_load.py`**

```python
import json
import sys


def load_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"Config file not found: {path}")
    except json.JSONDecodeError as error:
        raise SystemExit(f"{path} is not valid JSON (line {error.lineno}, column {error.colno}): {error.msg}")


path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
cfg = load_config(path)
print("loaded", len(cfg), "settings from", path)
```

Test the three cases. First, a good file:

```text
$ python exercises/day04/safe_load.py
loaded 14 settings from config.json
```

A file that does not exist:

```text
$ python exercises/day04/safe_load.py missing.json
Config file not found: missing.json
```

A file with a mistake. Create `exercises/day04/broken.json` with a comma after the last item:

**`exercises/day04/broken.json`**

```json
{
  "confidence": 0.45,
  "image_size": 640,
}
```

```text
$ python exercises/day04/safe_load.py exercises/day04/broken.json
exercises/day04/broken.json is not valid JSON (line 4, column 1): Expecting property name enclosed in double quotes
```

The message names the problem, the line and the column. This is what you want users (and future you) to see.

## Lab 4.3: Find the bug

This program should print the average confidence of the **person** detections. The real answer is `0.7` (that is `(0.9 + 0.7 + 0.5) / 3`). It prints something else. Do **not** read the code for a long time: use the debugger.

**`exercises/day04/debug_me.py`**

```python
detections = [("person", 0.9), ("car", 0.8), ("person", 0.7), ("person", 0.5)]


def average_confidence(items, label):
    total = 0
    count = 0
    for name, confidence in items:
        if name == label:
            total += confidence
        count += 1
    return total / count


average = average_confidence(detections, "person")
print("average person confidence:", round(average, 2))  # we expect 0.7
```

```text
$ python exercises/day04/debug_me.py
average person confidence: 0.53
```

1. Set a breakpoint on the line `if name == label:`.
2. Press F5. Press F10 many times. After each step look at `total` and `count`.
3. When `name` is `"car"`, what happens to `count`? Why is that wrong?
4. Fix the program.

<details><summary>Solution</summary>

`count += 1` is outside the `if`, so cars are counted too (`count` becomes 4 instead of 3). Move it **inside** the `if`:

**`exercises/day04/debug_me_fixed.py`**

```python
detections = [("person", 0.9), ("car", 0.8), ("person", 0.7), ("person", 0.5)]


def average_confidence(items, label):
    total = 0
    count = 0
    for name, confidence in items:
        if name == label:
            total += confidence
            count += 1  # count only the items we added
    return total / count


average = average_confidence(detections, "person")
print("average person confidence:", round(average, 2))  # 0.7
```

```text
$ python exercises/day04/debug_me_fixed.py
average person confidence: 0.7
```

</details>

## Check yourself

1. What is the difference between `except ValueError:` and a bare `except:`?
2. When does the `finally` block run?
3. What does pressing F10 do in the debugger?

<details><summary>Answers</summary>

1. The first catches only `ValueError`. The bare `except:` catches every error, even your own typos, and hides real problems.
2. Always: after the `try` block finishes, after an `except` block, and even when the program is stopping because of an error.
3. It runs the current line and stops at the next one (step over).

</details>

---

# Hour 12: Modules and packages (Milestone 1)

## Learn

### A file is a module

Any `.py` file can be **imported** by another one. You already did it with `import json`. You can also write your own. Create `exercises/day04/box_tools.py`:

**`exercises/day04/box_tools.py`**

```python
def box_width(box):
    x1, y1, x2, y2 = box
    return x2 - x1


def box_area(box):
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)


if __name__ == "__main__":
    # This part runs only when you start THIS file, not when another file imports it.
    assert box_width((10, 10, 50, 40)) == 40
    assert box_area((10, 10, 50, 40)) == 1200
    print("box_tools self-test passed")
```

and `exercises/day04/use_box_tools.py` next to it:

**`exercises/day04/use_box_tools.py`**

```python
from box_tools import box_area, box_width

person = (47, 400, 239, 904)
print("width:", box_width(person))
print("area:", box_area(person))
```

```text
$ python exercises/day04/use_box_tools.py
width: 192
area: 96768
```

There are three ways to import:

```pycon
>>> import math
>>> math.sqrt(16)
4.0
>>> from math import sqrt
>>> sqrt(25)
5.0
>>> import numpy as np
>>> np.arange(3)
array([0, 1, 2])
```

**`if __name__ == "__main__":`** In the file above, the last block runs only when you start **that** file directly. When another file imports it, the block is skipped. Python sets `__name__` to `"__main__"` for the file you started. Use this guard for the "start the program" part of a file:

```text
$ python exercises/day04/box_tools.py
box_tools self-test passed
```

### A package is a folder of modules

A folder with a file called `__init__.py` is a **package**. Our code lives in the package `intelligence/`:

```text
intelligence/
├── __init__.py     <- runs the first time anything is imported from the package
└── config.py       <- a module inside the package
```

From a script outside the package you import with the package name: `from intelligence.config import load_config`. Inside the package, modules can import each other with a **relative** import, where the leading dot means "this package": `from .config import load_config`. Today `config.py` only needs a value from `__init__.py`, so it will use `from . import PROJECT_ROOT`.

### Where is the project folder?

`config.py` must find `config.json` **no matter where you start the program from**. The trick: a file knows its own location in the variable `__file__`. From it we climb up to the project folder:

```pycon
>>> from pathlib import PurePosixPath
>>> path = PurePosixPath("/home/sokha/my-intelligence-system/intelligence/__init__.py")
>>> path.name
'__init__.py'
>>> path.parent
PurePosixPath('/home/sokha/my-intelligence-system/intelligence')
>>> path.parent.parent
PurePosixPath('/home/sokha/my-intelligence-system')
```

So in `intelligence/__init__.py`, `Path(__file__).resolve().parent.parent` is the project folder. (`resolve()` makes the path absolute. Windows paths work the same way, with backslashes.) We save it as `PROJECT_ROOT`. A small helper, `project_path`, then turns a relative path from `config.json` (like `data/events.db`) into an absolute path inside the project.

## Lab 4.4 (Milestone 1): The `intelligence` package

Create these files in your project folder. Copy the code from your `parse_env.py` for `load_env`, and add `load_config` and `project_path`.

**Step 1.** Create the folder `intelligence`, and the file `intelligence/__init__.py`:

**`intelligence/__init__.py`**

```python
"""Security camera intelligence system: detection, tracking, memory, rules, alerts."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
```

**Step 2.** Create `intelligence/config.py`:

**`intelligence/config.py`**

```python
import json
from pathlib import Path

from . import PROJECT_ROOT


def load_env(path):
    """Read KEY=VALUE lines from a .env file into a plain dict (nothing is exported)."""
    values = {}
    if not path.is_file():
        return values
    # utf-8-sig: Windows Notepad may save a BOM that would otherwise glue itself to the first key.
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(path=None):
    path = Path(path) if path else PROJECT_ROOT / "config.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def project_path(relative):
    """Resolve a config path against the project folder (absolute paths pass through)."""
    p = Path(relative)
    return p if p.is_absolute() else PROJECT_ROOT / p
```

Read it line by line:

- `load_env` is the function from hour 10.
- `load_config` opens `config.json` (or another file you give it) and returns the dictionary.
- `project_path` leaves absolute paths alone and puts relative paths inside the project folder.

**Step 3.** Create `security_camera.py` in the project folder (this is the program you will start on every later day). For now it only loads the settings and prints a summary:

**`security_camera.py`**

```python
from intelligence import PROJECT_ROOT
from intelligence.config import load_config, load_env, project_path


def main():
    cfg = load_config()
    env = load_env(PROJECT_ROOT / ".env")

    print("Watching:", ", ".join(cfg["watch_classes"]))
    print("Database file:", project_path(cfg["paths"]["database"]))
    print("Telegram token set:", bool(env.get("TELEGRAM_BOT_TOKEN")))
    print("Telegram chat id set:", bool(env.get("TELEGRAM_CHAT_ID")))


if __name__ == "__main__":
    main()
```

**Step 4.** Run it from the project folder:

```text
$ python security_camera.py
Watching: person, car, truck, bus, motorcycle, bicycle, dog, cat
Database file: /path/to/my-intelligence-system/data/events.db
Telegram token set: True
Telegram chat id set: True
```

Now run it **from another folder** to prove that it finds its files anywhere (replace the path with where your project is):

```bash
cd exercises
python ../security_camera.py
```

You should see the same output.

**Step 5.** Create a `tests` folder with an empty `tests/__init__.py` and the file `tests/check_config.py`. It is a self-check made of `assert` lines:

**`tests/check_config.py`**

```python
import tempfile
from pathlib import Path

from intelligence import PROJECT_ROOT
from intelligence.config import load_config, load_env, project_path

# load_env: comments and blank lines are skipped, quotes are removed, only the first "=" splits
with tempfile.TemporaryDirectory() as folder:
    env_file = Path(folder) / ".env"
    env_file.write_text('# comment\n\nTOKEN="abc=123"\nCHAT_ID = 42\nbroken line\n', encoding="utf-8")
    assert load_env(env_file) == {"TOKEN": "abc=123", "CHAT_ID": "42"}
assert load_env(Path("does-not-exist.env")) == {}

# project_path: relative paths start at the project folder, absolute paths are left alone
assert project_path("data/events.db") == PROJECT_ROOT / "data" / "events.db"
assert project_path(PROJECT_ROOT) == PROJECT_ROOT

# load_config: the real config.json has the settings we need
cfg = load_config()
for key in ("watch_classes", "label_severity", "night_hours", "alert", "paths"):
    assert key in cfg, f"config.json is missing {key!r}"

print("config OK")
```

Run it from the project folder with `-m`, which runs a module by its package path:

```text
$ python -m tests.check_config
config OK
```

If you see `config OK`, Milestone 1 is done. If an `assert` fails, read the line number, fix `config.py`, and run again.

## Check yourself (exit ticket)

1. What file makes a folder a package?
2. Why do we compute `PROJECT_ROOT` from `__file__` and not just write `"config.json"`?
3. What does `if __name__ == "__main__":` do?
4. `from .config import load_config` or `from intelligence.config import load_config`: which one do you write in a script outside the package?

<details><summary>Answers</summary>

1. `__init__.py`.
2. A relative path depends on where you start the program. `__file__` is always the real location of the code, so the project finds its files from any folder.
3. It runs the indented block only when the file is started directly, not when it is imported.
4. `from intelligence.config import load_config`. The dot form (relative import) only works inside the package.

</details>

---

# Day 4 wrap-up

## Checklist

- [ ] `.env` exists (fake values are fine), and `.env.example` exists.
- [ ] `python security_camera.py` prints the summary, from the project folder **and** from another folder.
- [ ] `python -m tests.check_config` prints `config OK`.
- [ ] You fixed `debug_me.py` using the debugger.
- [ ] You can explain what `__init__.py` and `__file__` are for.

## Your project folder today

```text
my-intelligence-system/
├── .env
├── .env.example
├── config.json
├── security_camera.py
├── intelligence/
│   ├── __init__.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   └── check_config.py
└── exercises/
    ├── day01/ ... day03/
    └── day04/
        ├── parse_env.py
        ├── safe_load.py
        ├── broken.json
        ├── debug_me.py
        ├── box_tools.py
        └── use_box_tools.py
```

Solutions are in [`solutions/day04/`](solutions/day04/).

## Instructor notes

- **The working folder** is the number one cause of "file not found" errors. Say it again every day: always run `python ...` from the project folder.
- **`__file__` and `.parent.parent`** feel like magic. Draw the folder tree on the board and walk up one level at a time, like the `PurePosixPath` demo.
- **Debugger:** students must try it themselves. Many will click Run instead of Debug; show the difference. If the red dot does not appear, the file may not be saved or the Python extension is not installed.
- **Windows:** `\` in paths. Show that `pathlib` makes it a non-issue. Warn about Notepad saving `.env` as `.env.txt`: students should create it in VS Code.
- **Secrets:** repeat that the token is never printed and never committed. Tomorrow's git lesson relies on this habit.
- **If you are behind:** Lab 4.3 (debugger) can be shortened to a demo. Milestone 1 (Lab 4.4) cannot be skipped.
- **Fast finishers:** make `load_env` ignore a leading `export ` word (`export TOKEN=abc`), or add a function `require(env, "TELEGRAM_BOT_TOKEN")` that stops with a clear message when a key is missing.

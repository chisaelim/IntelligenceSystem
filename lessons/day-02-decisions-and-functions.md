# Day 2: Decisions and functions

**Hours 4-6 of 45** · Project milestone: the first version of the "brain" (`assess`, how serious is a sighting?)

## What you can do at the end of today

- Write conditions with comparison and logic operators (`<`, `==`, `and`, `or`, `not`, `in`).
- Choose between actions with `if`, `elif` and `else`.
- Repeat work with `for` and `while` loops, and stop a loop with `break`.
- Write functions with parameters, default values and return values.
- Write a function that turns "a person is here" into a severity from 0 to 3.

## Where today fits in the project

The Intelligence System must decide **what matters**. A cat in the garden at noon is not worth a message. A person at the front door at 3 a.m. is. Today you write the first version of that decision as a Python function. On Day 14 the same idea grows into `rules.py`.

The camera program will also repeat the same steps again and again (read a frame, look at it, repeat). That is a loop. Today you practise the two loop patterns the project uses.

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 4 | 5 | Warm-up: two questions from the Day 1 exit ticket |
| | 15 | Talk: comparisons, `and`/`or`/`not`, `if`/`elif`/`else` |
| | 10 | Live demo in the console |
| | 25 | **Labs 2.1-2.2** Confidence classifier, night check |
| | 5 | Review |
| 5 | 15 | Talk: `for`, `while`, `break`, `%` |
| | 10 | Live demo |
| | 25 | **Labs 2.3-2.4** Frame counter, camera retry loop |
| | 10 | Review |
| 6 | 15 | Talk: functions, parameters, return values, scope |
| | 10 | Live demo |
| | 30 | **Lab 2.5** The severity function |
| | 5 | Exit ticket |

---

# Hour 4: Making decisions

## Learn

A **condition** is a question with the answer `True` or `False`. You build conditions with comparison operators:

| Operator | Means | Example |
|---|---|---|
| `==` | equal to | `label == "person"` |
| `!=` | not equal to | `label != "car"` |
| `<` `<=` | less than, less than or equal | `confidence < 0.45` |
| `>` `>=` | greater than, greater than or equal | `hour >= 22` |
| `in` | is one of | `label in ("car", "bus")` |

Combine conditions with `and`, `or` and `not`:

```pycon
>>> confidence = 0.62
>>> label = "person"
>>> confidence > 0.5
True
>>> confidence == 0.62
True
>>> label == "person"
True
>>> label != "car"
True
>>> label in ("person", "car")
True
>>> confidence > 0.5 and label == "person"
True
>>> confidence > 0.9 or label == "car"
False
>>> not (confidence > 0.9)
True
```

**Two traps.** First, `=` stores a value and `==` compares two values. Writing `if label = "person":` is a syntax error. Second, never compare decimals with `==`, because computers store them with tiny errors:

```pycon
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
>>> abs((0.1 + 0.2) - 0.3) < 0.000001
True
```

This is one reason the project uses thresholds such as `confidence >= 0.45` and never `confidence == 0.45`.

## `if`, `elif`, `else`

An `if` runs a block of code only when its condition is `True`. The block is **indented by 4 spaces**, and the line before it ends with a colon `:`. Python checks the conditions from top to bottom and runs **only the first one that is true**:

```pycon
>>> score = 0.62
>>> if score < 0.45:
...     print("ignore")
... elif score < 0.70:
...     print("medium")
... else:
...     print("high")
...
medium
```

The order matters. If you wrote `elif score < 0.90` first, a score of `0.62` would match it and the `0.70` check would never run. Always put the most specific condition first.

## Lab 2.1: Confidence classifier

A detector gives every object a **confidence** between 0 and 1. The project ignores anything below `0.45`. Write a program that asks for a confidence and answers `ignore`, `medium` or `high`.

Create `exercises/day02/confidence.py`:

**`exercises/day02/confidence.py`**

```python
CONFIDENCE_LIMIT = 0.45  # the same number as "confidence" in config.json

score = float(input("Detection confidence (0 to 1): "))

if score < CONFIDENCE_LIMIT:
    print("ignore: too uncertain")
elif score < 0.70:
    print("medium: probably correct")
else:
    print("high: very likely correct")
```

Try three values. Pay attention to the border value `0.45`: is it ignored or medium? Why?

```text
$ python exercises/day02/confidence.py
Detection confidence (0 to 1): 0.3
ignore: too uncertain
```

```text
$ python exercises/day02/confidence.py
Detection confidence (0 to 1): 0.45
medium: probably correct
```

```text
$ python exercises/day02/confidence.py
Detection confidence (0 to 1): 0.9
high: very likely correct
```

`0.45` is *not* less than `0.45`, so it moves on to the next check and is "medium". If you want to change which side the border value belongs to, change `<` to `<=`.

## Lab 2.2: Is it night?

The project raises the severity at night. For now, night is from 22:00 until 05:59. Think first: which operator joins the two conditions, `and` or `or`? A number cannot be at least 22 **and** less than 6 at the same time, so the answer is `or`.

**`exercises/day02/night_check.py`**

```python
hour = int(input("Hour of the day (0 to 23): "))

if hour >= 22 or hour < 6:
    print("night")
else:
    print("day")
```

Test the border hours: `22`, `23`, `0`, `5`, `6`, `12`.

```text
$ python exercises/day02/night_check.py
Hour of the day (0 to 23): 22
night
```

```text
$ python exercises/day02/night_check.py
Hour of the day (0 to 23): 5
night
```

```text
$ python exercises/day02/night_check.py
Hour of the day (0 to 23): 6
day
```

**Challenge:** change `or` to `and` and run `23` again. What happens, and why?

## Check yourself

1. What does `if 5 > 3 and "a" == "b":` do?
2. Which is right: `if hour = 22:` or `if hour == 22:`?
3. In the classifier, why is `elif score < 0.70` correct and does not need `score >= 0.45 and score < 0.70`?

<details><summary>Answers</summary>

1. The first part is true and the second is false, so `and` gives `False` and the block does not run.
2. `if hour == 22:`. A single `=` assigns, it does not compare.
3. Python only reaches the `elif` if the first condition was false, which means `score` is already 0.45 or more.

</details>

---

# Hour 5: Repeating work with loops

## Learn

A **loop** repeats a block of code. Python has two kinds.

**`for`** repeats for each item in a sequence. `range(n)` makes the numbers `0` to `n - 1`:

```pycon
>>> for number in range(3):
...     print("frame", number)
...
frame 0
frame 1
frame 2
>>> for number in range(1, 4):
...     print("frame", number)
...
frame 1
frame 2
frame 3
>>> for number in range(0, 10, 4):
...     print(number)
...
0
4
8
```

`range(start, stop, step)` stops **before** `stop`. This "stop is not included" rule is the most common source of off-by-one mistakes.

You can loop over any group of items, and add up values as you go (an **accumulator**):

```pycon
>>> total = 0
>>> for confidence in (0.9, 0.8, 0.7):
...     total += confidence
...
>>> total
2.4000000000000004
>>> round(total / 3, 2)
0.8
```

`total += x` is short for `total = total + x`. Notice the small decimal error again (`2.4000000000000004`), which is why we use `round()` or `:.2f` when we show numbers.

**`while`** repeats **as long as** a condition is true. Use it when you do not know in advance how many times:

```pycon
>>> battery = 3
>>> while battery > 0:
...     print("battery", battery)
...     battery -= 1
...
battery 3
battery 2
battery 1
>>> print("battery empty")
battery empty
```

If the condition never becomes false, the loop never stops (an *infinite loop*). Press **Ctrl+C** to stop it.

Two keywords control a loop from the inside:

- `break` leaves the loop immediately.
- `continue` skips the rest of this round and goes to the next one.

```pycon
>>> for number in range(1, 10):
...     if number % 2 == 0:
...         continue
...     if number > 7:
...         break
...     print(number)
...
1
3
5
7
```

**The remainder trick.** `number % 30 == 0` is true for every 30th number. The project uses `%` for "do something every N frames".

**The camera pattern.** The most important loop of the whole project looks like this. On Day 8 you will write it for real:

```python
while True:            # forever
    frame = read_the_camera()
    if frame is missing:
        wait a little and try again
    process(frame)
    if the user pressed "q":
        break          # the only way out
```

## Lab 2.3: Count frames

A camera makes 30 frames per second. Print a message each time a full second has passed, for 3 seconds. Use a `for` loop and `%`.

**`exercises/day02/frames_loop.py`**

```python
FPS = 30
SECONDS = 3

for frame_number in range(1, FPS * SECONDS + 1):
    if frame_number % FPS == 0:
        print(f"{frame_number // FPS} second(s) passed, {frame_number} frames read")
```

```text
$ python exercises/day02/frames_loop.py
1 second(s) passed, 30 frames read
2 second(s) passed, 60 frames read
3 second(s) passed, 90 frames read
```

**Try:** change `SECONDS` to `10` and `FPS` to `15`.

## Lab 2.4: Camera retry loop

A webcam sometimes fails to give a frame (it is starting, or another app is using it). A good program waits and tries again, but not forever. Here the "camera" is a pretend function that fails twice and then works.

**`exercises/day02/retry_loop.py`**

```python
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
```

```text
$ python exercises/day02/retry_loop.py
Camera read failed (attempt 1), retrying...
Camera read failed (attempt 2), retrying...
Got a frame after 3 attempt(s)
```

Read the loop condition: `attempt < MAX_ATTEMPTS and not got_frame`. The loop continues while we still have attempts left **and** we have no frame yet.

**Try:** change `attempt >= 3` to `attempt >= 9` in `read_frame`. The camera now never answers within 5 attempts, so the program prints `Camera did not respond, giving up`.

## Check yourself

1. How many times does `for i in range(5):` run? What is the last value of `i`?
2. What is the difference between `break` and `continue`?
3. Which loop would you use to "keep asking until the user types `q`"?

<details><summary>Answers</summary>

1. 5 times. The last value is 4 (it starts at 0).
2. `break` leaves the whole loop. `continue` skips only the rest of the current round.
3. A `while` loop, because we do not know how many times it will run.

</details>

---

# Hour 6: Functions

## Learn

A **function** is a named block of code that you can run again and again. You define it with `def`, and you **call** it by writing its name with brackets. A function can take **parameters** (inputs) and **return** a value (output):

```pycon
>>> def to_percent(confidence):
...     return round(confidence * 100)
...
>>> to_percent(0.874)
87
>>> to_percent(0.5)
50
```

Parameters can have **default values**. When you call a function you can pass values by position or by name:

```pycon
>>> def describe(label, confidence=0.5):
...     return f"{label} ({confidence:.0%})"
...
>>> describe("person")
'person (50%)'
>>> describe("person", 0.91)
'person (91%)'
>>> describe(confidence=0.3, label="car")
'car (30%)'
```

**`print` is not `return`.** `print` shows something on the screen. `return` hands a value back to the code that called the function. A function without `return` gives back `None`:

```pycon
>>> def show(x):
...     print("value is", x)
...
>>> result = show(3)
value is 3
>>> print(result)
None
>>> def double(x):
...     return x * 2
...
>>> double(3) + 1
7
```

**Scope.** Variables created inside a function exist only inside it:

```pycon
>>> def make_message():
...     message = "hello"
...     return message
...
>>> make_message()
'hello'
>>> print(message)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'message' is not defined
```

**Early return.** A function can stop early with `return`. The project uses this to handle special cases first ("a dog is never an alert"), so the rest of the function stays simple. It is called a *guard clause*.

**Docstrings and asserts.** A string on the first line of a function is its **docstring**: a short note on what it does. An `assert` line is a quick self-test: if the condition is false, Python stops with `AssertionError`. You will write many asserts in this course.

## Lab 2.5: The severity function

Write the first version of the brain. The rules (from the project's design):

| Rule | Points |
|---|---|
| A **person** | base 2 |
| A **car, truck, bus, motorcycle or bicycle** | base 1 |
| Anything else (a dog, a cat) | base 0, and 0 means "log it, never alert" |
| It is **night** | +1 |
| It is **inside a zone** | +1 |
| The maximum | 3 |

Build it in three small steps. Create `exercises/day02/severity.py`:

1. Write `base_severity(label)` with `if`/`elif`/`else`. Test it by calling it with a few labels.
2. Write `assess(label, at_night=False, in_zone=False)`. If the base is 0, return 0 at once. Otherwise add the points and return the smaller of the total and 3. (`min(a, b)` gives the smaller one.)
3. Write `severity_name(severity)` to turn `0, 1, 2, 3` into `ignored`, `low`, `medium`, `HIGH`. Finish with the `assert` lines and the `print` lines.

**`exercises/day02/severity.py`**

```python
def base_severity(label):
    """How serious is this kind of object on its own? 0 means 'log it, never alert'."""
    if label == "person":
        return 2
    elif label in ("car", "truck", "bus", "motorcycle", "bicycle"):
        return 1
    else:
        return 0


def assess(label, at_night=False, in_zone=False):
    """Return a severity from 0 to 3."""
    score = base_severity(label)
    if score == 0:
        return 0
    if at_night:
        score = score + 1
    if in_zone:
        score = score + 1
    return min(score, 3)


def severity_name(severity):
    if severity == 0:
        return "ignored"
    elif severity == 1:
        return "low"
    elif severity == 2:
        return "medium"
    else:
        return "HIGH"


# Quick checks. If one of them is wrong, Python stops with an AssertionError.
assert assess("person") == 2
assert assess("person", at_night=True) == 3
assert assess("car") == 1
assert assess("car", at_night=True, in_zone=True) == 3
assert assess("dog", at_night=True, in_zone=True) == 0
assert assess("person", at_night=True, in_zone=True) == 3  # capped at 3

print("person, daytime  :", severity_name(assess("person")))
print("person, at night :", severity_name(assess("person", at_night=True)))
print("car, daytime     :", severity_name(assess("car")))
print("car, night + zone:", severity_name(assess("car", at_night=True, in_zone=True)))
print("dog, anything    :", severity_name(assess("dog", at_night=True, in_zone=True)))
```

```text
$ python exercises/day02/severity.py
person, daytime  : medium
person, at night : HIGH
car, daytime     : low
car, night + zone: HIGH
dog, anything    : ignored
```

If an `assert` line fails you will see an `AssertionError` with the line number. Fix the function, not the test.

**Challenge:** add a third parameter `unusual=False`. If it is true, add one more point. (On Day 14 the real project adds "unusual for this hour".)

## Check yourself (exit ticket)

1. What is the difference between `print(x)` and `return x`?
2. What does this print? `def f(a, b=2): return a * b` then `print(f(3), f(3, 4))`
3. Why does `assess("dog", at_night=True, in_zone=True)` return 0 and not 3?
4. What is a guard clause?

<details><summary>Answers</summary>

1. `print` shows the value on the screen and the function still returns `None`. `return` gives the value back to the caller so you can use it.
2. `6 12`.
3. A dog has base severity 0, and the function returns 0 immediately before adding night or zone points.
4. An early `return` (or `continue`) at the top of a function that handles a special case first, so the rest of the code does not need to worry about it.

</details>

## Homework (optional, 15 minutes)

Write a function `is_night(hour)` that returns `True` or `False`, then use it to test the hours `0, 5, 6, 12, 21, 22, 23`.

<details><summary>Solution</summary>

**`exercises/day02/is_night_hour.py`**

```python
def is_night(hour):
    """True from 22:00 until 05:59."""
    return hour >= 22 or hour < 6


for hour in (0, 5, 6, 12, 21, 22, 23):
    print(hour, "->", is_night(hour))
```

```text
$ python exercises/day02/is_night_hour.py
0 -> True
5 -> True
6 -> False
12 -> False
21 -> False
22 -> True
23 -> True
```

</details>

---

# Day 2 wrap-up

## Checklist

- [ ] `confidence.py` prints `ignore`, `medium` or `high` correctly, including the border value `0.45`.
- [ ] `night_check.py` is right for `22`, `5` and `6`.
- [ ] `frames_loop.py` and `retry_loop.py` run.
- [ ] `severity.py` runs with no `AssertionError`.
- [ ] You can explain the difference between `print` and `return`.

## Today you built

```text
my-intelligence-system/
└── exercises/
    └── day02/
        ├── confidence.py
        ├── night_check.py
        ├── frames_loop.py
        ├── retry_loop.py
        ├── severity.py
        └── is_night_hour.py   (homework)
```

Solutions are in [`solutions/day02/`](solutions/day02/).

## Instructor notes

- **Warm-up (hour 4):** ask two exit-ticket questions from Day 1 before starting. It shows who is lost early.
- **Typical mistakes:** a missing colon after `if`, wrong indentation (mixing tabs and spaces: tell VS Code to use 4 spaces), `=` instead of `==`, forgetting `float(...)` around `input()`, and an infinite `while` loop (teach Ctrl+C).
- **Make students predict.** Before running `frames_loop.py`, ask what the first and last lines will be. Predicting output is the fastest way to learn loops.
- **Debug with `print`.** Show students how to add `print(attempt, got_frame)` inside the retry loop to see what changes each round. Day 4 adds the real debugger.
- **If you are behind:** skip the "Challenge" lines. Do not skip Lab 2.5: Day 3 builds on it directly.
- **Fast finishers:** a "traffic light" function that returns `"red"`, `"yellow"` or `"green"` from a number of seconds; or the `unusual` challenge.

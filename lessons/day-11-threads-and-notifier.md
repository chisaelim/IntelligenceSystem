# Day 11: Not blocking the camera

**Hours 31-33 of 45** · **Milestone 6:** `TelegramNotifier` (alerts sent from a background thread)

## What you can do at the end of today

- Explain why a slow network call freezes a video loop.
- Use `threading.Thread`, `queue.Queue` and `threading.Event`.
- Write the worker-thread pattern: the main loop puts jobs in a queue, a helper thread does them.
- Write and test `TelegramNotifier`, with a `--dry-run` mode and safe error handling.

## Where today fits in the project

Sending a photo to Telegram takes time: the internet may need a second or two, or ten if the connection is bad. If the camera loop waits for it, the video **freezes** and the camera misses things while it waits. A security camera that goes blind every time it sends an alert is not a security camera.

The fix is a classic pattern: the main loop only **drops the message in a queue** (this takes a microsecond) and a **second thread** takes messages out of the queue and sends them, as slowly as it needs to.

```text
 main thread (camera loop)                          worker thread
 ───────────────────────────                        ──────────────────────
  read frame → detect → alert!                       wait for a message
        │                                             │
        └─ notifier.send_photo(...) ──► [ queue ] ──► requests.post(...)  (slow, but nobody waits)
        keep reading frames                           then wait for the next message
```

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 31 | 5 | Warm-up: what does status `401` mean? |
| | 15 | Talk: blocking, threads, queues, events |
| | 10 | Live demo of the freeze |
| | 30 | **Labs 11.1-11.2** See the freeze, fix it with a worker thread |
| 32 | 15 | Talk: the design of `TelegramNotifier` |
| | 45 | **Lab 11.3 (Milestone 6)** Write the notifier and its test |
| 33 | 10 | Talk: dry-run mode and error handling |
| | 30 | **Lab 11.4** Test with `--dry-run`, then with your real bot |
| | 20 | Review, group discussion: what can still go wrong? |

---

# Hour 31: Why we need threads

## Learn

A normal program does **one thing at a time**. When it calls a slow function (a network request, `time.sleep`), the whole program **waits**. This waiting is called **blocking**.

A **thread** is a second line of execution inside the same program. Two threads can both be "waiting" or "working" at the same time. Python has the module `threading`:

```pycon
>>> import threading
>>> import time
>>> def hello(name):
...     time.sleep(0.1)
...     print("hello from", name)
...
>>> t = threading.Thread(target=hello, args=("the worker",))
>>> t.start()
>>> print("main goes on")
main goes on
>>> t.join()
hello from the worker
```

- `Thread(target=function, args=(...))` prepares a thread. `start()` begins it.
- The main program did **not** wait: `main goes on` was printed first, and the thread printed 0.1 seconds later.
- `join()` makes the main program wait until the thread is finished.

### A queue to pass messages

Two threads must not share data carelessly. The safe way to hand work from one thread to another is a **queue**. The module `queue` has `queue.Queue`, a **thread-safe** line: one side `put`s items in, the other side `get`s them out in the same order. `get()` **waits** if the queue is empty.

```pycon
>>> import queue
>>> q = queue.Queue()
>>> q.put("first")
>>> q.put("second")
>>> q.get()
'first'
>>> q.get()
'second'
>>> q.empty()
True
```

### An event to say "I am done"

A `threading.Event` is a flag that threads can wait for. `wait()` blocks until another thread calls `set()`:

```pycon
>>> import threading
>>> done = threading.Event()
>>> done.is_set()
False
>>> done.set()
>>> done.is_set()
True
>>> done.wait(timeout=1)
True
```

### Daemon threads

A thread started with `daemon=True` is a **background** thread: it is stopped automatically when the main program ends. Without it, the program would never exit while the worker is still waiting on its queue. The price: anything still unsent in the queue at that moment is **lost**. That is why the notifier has a `flush()` method, which the program calls before it quits.

### A word about Python and speed

Because of how Python works, two threads do not calculate faster than one. Threads help when a program is **waiting** (for the network, a disk, a camera), which is exactly the case here. They do not make heavy maths faster.

## Lab 11.1: See the freeze

Create `exercises/day11/freeze_demo.py`. It pretends to be a camera loop at 20 frames per second. At frame 5 something happens and the loop sends an alert with a function that needs 2 seconds (like a slow network). The program measures the **longest pause between two frames**.

**`exercises/day11/freeze_demo.py`**

```python
import time

FRAME_TIME = 0.05  # a "camera" that makes 20 frames per second


def send_alert_slowly():
    """Pretend network call: the server needs 2 seconds to answer."""
    time.sleep(2.0)


last_frame = time.perf_counter()
longest_gap = 0.0

for frame_number in range(1, 61):  # 3 seconds of video
    time.sleep(FRAME_TIME)  # waiting for the camera
    now = time.perf_counter()
    longest_gap = max(longest_gap, now - last_frame)
    last_frame = now

    if frame_number == 5:
        print("frame 5: something happened, sending an alert...")
        send_alert_slowly()  # the whole program waits here!
        print("   (alert sent)")

print(f"longest pause between two frames: {longest_gap:.2f} seconds")
```

Run it. The numbers vary a little from run to run, but you should see something like this:

```text
$ python exercises/day11/freeze_demo.py
frame 5: something happened, sending an alert...
   (alert sent)
longest pause between two frames: 2.06 seconds
```

For 2 seconds the loop read **no frames**. A person could walk through the door in that time.

## Lab 11.2: Fix it with a worker thread

Create `exercises/day11/worker_demo.py`. It is the same loop, but the alert goes into a queue and a daemon thread sends it:

**`exercises/day11/worker_demo.py`**

```python
import queue
import threading
import time

FRAME_TIME = 0.05  # a "camera" that makes 20 frames per second
alerts = queue.Queue()


def send_alert_slowly(text):
    """Pretend network call: the server needs 2 seconds to answer."""
    time.sleep(2.0)
    print(f"   (alert sent: {text})")


def worker():
    while True:
        text = alerts.get()  # waits here until there is something to send
        send_alert_slowly(text)


threading.Thread(target=worker, daemon=True).start()

last_frame = time.perf_counter()
longest_gap = 0.0

for frame_number in range(1, 61):  # 3 seconds of video
    time.sleep(FRAME_TIME)  # waiting for the camera
    now = time.perf_counter()
    longest_gap = max(longest_gap, now - last_frame)
    last_frame = now

    if frame_number == 5:
        print("frame 5: something happened, queueing an alert...")
        alerts.put("person at the door")  # takes almost no time, the loop goes on

print(f"longest pause between two frames: {longest_gap:.2f} seconds")
```

Typical output:

```text
$ python exercises/day11/worker_demo.py
frame 5: something happened, queueing an alert...
   (alert sent: person at the door)
longest pause between two frames: 0.06 seconds
```

The alert is still sent (2 seconds later, from the worker), but the loop never stopped: the longest pause is just the normal 0.05 seconds between frames. The camera never went blind.

Read how the worker waits: `alerts.get()` blocks **inside the worker thread**, so nobody else is blocked.

**Try:** queue three alerts at frames 5, 6 and 7. They are sent one after another, in order, because there is one worker.

## Check yourself

1. What does "blocking" mean?
2. Why do we use a `Queue` between the threads?
3. What happens to messages that are still in the queue when the program ends (with a daemon thread)?

<details><summary>Answers</summary>

1. The program stops and waits for a slow operation to finish, so it cannot do anything else meanwhile.
2. It is a safe, ordered way to pass work from one thread to another, and `get()` waits when there is nothing to do.
3. They are lost, because the daemon thread is stopped with the program. That is why we wait with `flush()` before quitting.

</details>

---

# Hour 32: Building `TelegramNotifier` (Milestone 6)

## Learn: the design

The notifier is a class with three public methods:

| Method | What it does | Who calls it |
|---|---|---|
| `send_text(text)` | puts a text message in the queue | the camera loop |
| `send_photo(path, caption)` | puts a photo message in the queue | the camera loop |
| `flush()` | waits until everything in the queue has been sent | the program, before quitting |

Inside, one worker thread takes items out of the queue. Each item is a tuple `(method, data, extra)`: the Telegram method name (`sendMessage`, `sendPhoto`), the form values, and the photo path (or something special).

**How does `flush` know the queue is empty?** It puts a special **marker** in the queue that carries an `Event`. The worker handles items in order, so when it reaches the marker, everything before it has been sent. It then calls `set()` on the event, and `flush` stops waiting. This trick uses the queue for what it is good at: order.

## Lab 11.3 (Milestone 6): Write the notifier

Create `intelligence/telegram_bot.py`:

**`intelligence/telegram_bot.py`**

```python
import queue
import threading

import requests


class TelegramNotifier:
    """Sends alerts from a background thread so the video loop never waits on the network."""

    def __init__(self, token, chat_id, dry_run=False):
        self.token = token
        self.chat_id = chat_id
        self.dry_run = dry_run
        self._queue = queue.Queue()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def send_text(self, text):
        self._queue.put(("sendMessage", {"text": text}, None))

    def send_photo(self, path, caption):
        self._queue.put(("sendPhoto", {"caption": caption[:1024]}, path))

    def flush(self, timeout=15):
        """Wait for queued messages to go out (used on shutdown)."""
        done = threading.Event()
        self._queue.put(("flush", None, done))
        done.wait(timeout)

    def _run(self):
        while True:
            method, data, extra = self._queue.get()
            if method == "flush":
                extra.set()
                continue
            if self.dry_run:
                print(f"[telegram dry-run] {method}: {data.get('text') or data.get('caption')}")
                continue
            try:
                url = f"https://api.telegram.org/bot{self.token}/{method}"
                data = {"chat_id": self.chat_id, **data}
                if method == "sendPhoto":
                    with open(extra, "rb") as f:
                        resp = requests.post(url, data=data, files={"photo": f}, timeout=20)
                else:
                    resp = requests.post(url, data=data, timeout=10)
                if not resp.ok:
                    print(f"[telegram] {method} failed: {resp.status_code} {resp.text}")
            except (requests.RequestException, OSError) as e:
                print(f"[telegram] {method} error: {type(e).__name__}")
```

Read it part by part.

**The constructor.** It stores the token and the chat id, creates the `Queue`, and starts the worker thread (`daemon=True`) right away. `dry_run=True` means "print, do not send".

**The two public methods.** They only call `self._queue.put(...)`: no network, so they return at once. `caption[:1024]` cuts a long caption to Telegram's limit.

**`flush`.** It creates an `Event`, puts the `"flush"` marker with that event in the queue, and waits up to `timeout` seconds for the worker to set it.

**`_run`, the worker loop.** `while True`: take the next item. In order:

1. If it is the flush marker: set the event and carry on.
2. If we are in dry-run mode: print what would be sent and carry on.
3. Otherwise send it with `requests.post(...)`:
   - `data = {"chat_id": self.chat_id, **data}` builds one dictionary from the chat id and the other values (`**` unpacks a dictionary into another).
   - A text goes as `data=...` with a `timeout` of 10 seconds. A photo opens the file in `"rb"` mode and goes as `files={"photo": f}` with a timeout of 20.
   - If Telegram answers with an error status (`not resp.ok`) the worker prints the status and Telegram's answer. The answer never contains your token.
   - If the network fails or the file cannot be opened, the `except` prints only the **type** of the error (like on Day 10: the full message contains the token).

The most important property: **an error never stops the worker.** One failed message is reported and the loop goes on with the next.

## The test

How do you test code that sends messages to the internet without spamming yourself? You **replace the network with a fake**. `unittest.mock.patch("requests.post", fake_post)` swaps `requests.post` with your own function while the test runs. The test checks four things:

1. In dry-run mode nothing goes to the network, and the text is printed.
2. In real mode the **URL and the data** are right, `send_text` returns at once (even though the fake network is slow), `flush` waits until the message has gone out, and long captions are cut to 1024 characters.
3. If the network fails, the worker survives and the token is never printed.
4. If Telegram answers `401`, it is reported without the token.

Create `tests/check_notifier.py`:

**`tests/check_notifier.py`**

```python
import io
import time
from contextlib import redirect_stdout
from unittest import mock

import requests

from intelligence.telegram_bot import TelegramNotifier

# 1. Dry run: nothing goes to the network, the text is printed instead
with mock.patch("requests.post") as post:
    out = io.StringIO()
    with redirect_stdout(out):
        notifier = TelegramNotifier("TOKEN", "42", dry_run=True)
        notifier.send_text("hello")
        notifier.send_photo(__file__, "a caption")
        notifier.flush()
    assert post.call_count == 0
    assert "hello" in out.getvalue() and "a caption" in out.getvalue()

# 2. Real mode, with the network replaced by a slow fake: the right URL and data are used,
#    sending returns at once, and flush() waits until the message has really gone out
calls = []


def slow_post(url, data=None, files=None, timeout=None):
    time.sleep(0.3)  # a slow network
    calls.append((url, data, files is not None, timeout))
    return mock.Mock(ok=True)


with mock.patch("requests.post", slow_post):
    notifier = TelegramNotifier("TOKEN", "42")

    start = time.monotonic()
    notifier.send_text("hello")
    assert time.monotonic() - start < 0.1, "send_text must return at once, not wait for the network"
    assert calls == [], "the message should still be on its way"

    notifier.flush()
    assert len(calls) == 1, "flush must wait until the message has gone out"
    url, data, has_files, timeout = calls[0]
    assert url == "https://api.telegram.org/botTOKEN/sendMessage"
    assert data == {"chat_id": "42", "text": "hello"}
    assert not has_files

    notifier.send_photo(__file__, "x" * 2000)  # a caption that is too long
    notifier.flush()
    url, data, has_files, timeout = calls[1]
    assert url.endswith("/sendPhoto") and has_files
    assert len(data["caption"]) == 1024, "captions are cut to Telegram's limit"

# 3. When the network fails, the worker survives and the token is never printed
def failing_post(*args, **kwargs):
    raise requests.ConnectionError("failed: https://api.telegram.org/botTOKEN/sendMessage")


with mock.patch("requests.post", failing_post):
    out = io.StringIO()
    with redirect_stdout(out):
        notifier = TelegramNotifier("TOKEN", "42")
        notifier.send_text("one")
        notifier.send_text("two")  # still processed after the first one failed
        notifier.flush()
    assert out.getvalue().count("ConnectionError") == 2
    assert "TOKEN" not in out.getvalue()


# 4. A rejected request (for example a wrong token) is reported, without the token
def rejected_post(*args, **kwargs):
    return mock.Mock(ok=False, status_code=401, text="Unauthorized")


with mock.patch("requests.post", rejected_post):
    out = io.StringIO()
    with redirect_stdout(out):
        notifier = TelegramNotifier("TOKEN", "42")
        notifier.send_text("hello")
        notifier.flush()
    assert "401" in out.getvalue() and "TOKEN" not in out.getvalue()

print("notifier OK")
```

```text
$ python -m tests.check_notifier
notifier OK
```

If you see `notifier OK`, Milestone 6 is done.

## Check yourself

1. Why does `send_text` return immediately?
2. How does `flush` know that all earlier messages were sent?
3. Why does the test replace `requests.post` with a fake?

<details><summary>Answers</summary>

1. It only puts the message in a queue. The slow sending is done by the worker thread.
2. It queues a marker holding an `Event`. The worker handles items in order, so when it reaches the marker everything before it has been processed, and it sets the event.
3. To test our code without a real network, a real token, or real messages, and so that we can make the network slow or broken on purpose.

</details>

---

# Hour 33: Dry run and safe errors

## Learn

A **dry run** runs the real program but replaces the dangerous or costly action with a printout. Our notifier prints `[telegram dry-run] ...` instead of sending. Why it is useful:

- You can test the whole camera program **without spamming** your phone.
- It works without a token (before Day 10 is done, or on a student's computer that has no bot).
- It is safe in front of a class.

The final program (Day 15) gets a `--dry-run` flag that passes `dry_run=True` to the notifier. Today you add that flag to a small test tool.

**What errors can happen when sending?**

| Problem | What the notifier does |
|---|---|
| No internet, DNS failure, timeout | `except` prints the error **type**; the worker goes on |
| Telegram says `401` / `400` / `429` | prints the status and Telegram's answer |
| The photo file is missing | `OSError` is caught and reported |
| The program ends while messages are queued | `flush()` must be called first |

**Known limit:** if the network is down for a long time, messages pile up in the queue and each one has to wait for its timeout. A real product would cap the queue or drop old alerts. You can try that as an extension.

## Lab 11.4: Test with `--dry-run`, then for real

Create `tools/notify_test.py`. It sends a text, and a photo if you give one, through `TelegramNotifier`:

**`tools/notify_test.py`**

```python
"""Send a test message (and a photo) through TelegramNotifier, the class the camera will use.

    python -m tools.notify_test --dry-run                   print what would be sent
    python -m tools.notify_test                             really send (needs .env)
    python -m tools.notify_test --photo output/day07_overlay.jpg
"""
import argparse

from intelligence import PROJECT_ROOT
from intelligence.config import load_env
from intelligence.telegram_bot import TelegramNotifier


def main():
    ap = argparse.ArgumentParser(description="Send a test alert through TelegramNotifier")
    ap.add_argument("--dry-run", action="store_true", help="print the alert instead of sending it")
    ap.add_argument("--photo", help="a picture to send with a caption")
    args = ap.parse_args()

    env = load_env(PROJECT_ROOT / ".env")
    token, chat_id = env.get("TELEGRAM_BOT_TOKEN", ""), env.get("TELEGRAM_CHAT_ID", "")
    if not args.dry_run and (not token or not chat_id):
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the .env file (or use --dry-run).")

    notifier = TelegramNotifier(token, chat_id, dry_run=args.dry_run)
    print("Queueing the messages...")
    notifier.send_text("Test message from the notifier")
    if args.photo:
        notifier.send_photo(args.photo, "Test alert: person, at night\n2026-01-01 12:00:00  (person #1)")

    notifier.flush()  # wait until everything has really gone out
    print("Done.")


if __name__ == "__main__":
    main()
```

First the dry run. Nothing leaves your computer and no token is needed:

```text
$ python -m tools.notify_test --dry-run --photo output/day07_overlay.jpg
Queueing the messages...
[telegram dry-run] sendMessage: Test message from the notifier
[telegram dry-run] sendPhoto: Test alert: person, at night
2026-01-01 12:00:00  (person #1)
Done.
```

Now for real, with your own bot (this uses the token and chat id from `.env`):

```bash
python -m tools.notify_test --photo output/day07_overlay.jpg
```

Your phone should receive the text and then the photo with its caption. Notice how fast `Done.` appears after `Queueing the messages...`: the main program only queued the work, and `flush()` waited for the worker.

What does a wrong token look like when it goes through the notifier? Here is the same tool with a fake token. The worker reports the problem and the program still finishes normally. **It does not crash:**

```text
$ python -m tools.notify_test
Queueing the messages...
[telegram] sendMessage failed: 401 {"ok":false,"error_code":401,"description":"Unauthorized"}
Done.
```

**Try:**

1. Remove the line `notifier.flush()` and run the real test. Does the message still arrive? (It may not: the program can end before the worker finishes.)
2. Use a photo path that does not exist, in real mode. What is printed?

## Check yourself (exit ticket)

1. What is a dry run, and why is it useful?
2. Name two things that can go wrong when sending, and say how the notifier handles each.
3. Why must the program call `flush()` before it quits?
4. Can a failing message stop the other messages? Why not?

<details><summary>Answers</summary>

1. Running the real program but printing the risky action (sending) instead of doing it. It lets you test safely, without spam, and without secrets.
2. For example: the network is down (the error type is printed and the worker continues), Telegram answers `401` (the status and answer are printed, and the worker continues).
3. The worker is a daemon thread: when the program ends, it stops, and anything still in the queue is lost.
4. No. The `try/except` is **inside** the worker's `while True` loop, so each message is handled on its own and the loop always continues.

</details>

## Homework (optional, 30 minutes)

Add a method `send_text_with_retry` idea on paper: if sending fails with a network error, how many times would you try again, and how long would you wait between tries (1 s, 2 s, 4 s?). Why is waiting longer each time a good idea? (You do not need to write the code.)

---

# Day 11 wrap-up

## Checklist

- [ ] `freeze_demo.py` shows a pause of about 2 seconds and `worker_demo.py` shows a pause of about 0.05 seconds.
- [ ] `python -m tests.check_notifier` prints `notifier OK`.
- [ ] `python -m tools.notify_test --dry-run` prints the dry-run lines and `Done.`
- [ ] A real message (and photo) reaches your phone through `TelegramNotifier`.
- [ ] You can explain the queue, the worker and `flush` to a classmate.
- [ ] You committed (`git commit -m "Day 11: TelegramNotifier"`).

## Your project folder today

```text
my-intelligence-system/
├── intelligence/
│   ├── telegram_bot.py         <- new: TelegramNotifier
│   └── ...
├── tools/
│   └── notify_test.py          <- new
├── tests/
│   └── check_notifier.py       <- new
└── exercises/day11/
    ├── freeze_demo.py
    └── worker_demo.py
```

Solutions are in [`solutions/day11/`](solutions/day11/).

## Instructor notes

- **Threads feel abstract.** The freeze demo is the whole lesson: run it live and let students feel the two-second pause, then run the fixed version. Ask: "Where was the camera during those 2 seconds?"
- **Do not go into locks, race conditions or the GIL.** Say only: "a queue is the safe way to pass work between threads."
- **The `flush` marker** is clever but confusing at first. Draw the queue as a row of boxes: `[text][photo][FLUSH]`.
- **Mocking:** students will not write `mock.patch` themselves yet. It is enough that they read the test and understand that "the network is replaced by a fake that we control".
- **Real bot test:** if a student's Telegram setup from Day 10 is not finished, they use `--dry-run` today and finish the bot at home. Today's code does not depend on a real bot.
- **If you are behind:** run Lab 11.1 and 11.2 as one demo. Milestone 6 (the file and its test) is needed on Day 15.
- **Fast finishers:** cap the queue with `queue.Queue(maxsize=10)` and decide what to do when it is full (drop the oldest alert, or the new one); or add a `send_text_with_retry`.

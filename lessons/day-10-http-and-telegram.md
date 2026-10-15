# Day 10: Talking to Telegram

**Hours 28-30 of 45** · Milestone: your own Telegram bot, a working `.env`, and a photo on your phone sent from Python · **Checkpoint 2** (NumPy, OpenCV, SQL, HTTP)

## What you can do at the end of today

- Explain HTTP: URL, request, response, status code, JSON.
- Use the `requests` library to call a web API (`get` and `post`), with a timeout and error handling.
- Create your own Telegram bot with BotFather and find your chat id.
- Send a text message and a photo from Python.
- Keep your token secret in `.env`, and know what to do if it leaks.

## Where today fits in the project

The last step of the Intelligence System is the alert: a photo and a sentence on your phone. Telegram offers this for free through a **Bot API**, which is plain HTTP. Today you learn HTTP, create the bot, and send your first photo. On Day 11 you wrap this into the class that the camera uses.

```text
 ... → severity ≥ 2? → snapshot.jpg → [ requests.post(...sendPhoto) ] → Telegram → your phone
                                          ▲ today
```

## Plan for the day

| Hour | Minutes | Activity |
|---|---|---|
| 28 | 5 | Warm-up: what does `?` do in a SQL statement? |
| | 20 | Talk: HTTP, URLs, status codes, JSON, `requests` |
| | 10 | Live demo |
| | 25 | **Labs 10.1-10.2** Call a public API, see errors |
| 29 | 15 | Talk: bots and the Bot API |
| | 45 | **Labs 10.3-10.4** Create the bot, find the chat id, send a message |
| 30 | 15 | Talk: secrets, `os.environ`, `sendPhoto` |
| | 10 | **Lab 10.5** Send a photo |
| | 20 | **Checkpoint 2** (quiz) |
| | 15 | Review the quiz answers |

**Before class:** every student needs a Telegram account (phone or desktop app).

---

# Hour 28: HTTP and the `requests` library

## Learn

**HTTP** is how programs talk over the web. A **client** (your program) sends a **request**; a **server** sends back a **response**. A web page, a weather app and the Telegram Bot API all work this way.

### A URL

```text
https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=123&text=hi
└─┬──┘   └──────┬───────┘└────┬────┘└────┬──────┘└──────────┬──────┘
scheme       host         path (what)   method name       query (extra values)
```

The **query** part (after `?`) carries values as `name=value` pairs joined with `&`. Spaces and special characters must be **encoded**. `requests` does this for you:

```pycon
>>> import requests
>>> prepared = requests.Request("GET", "https://example.com/search", params={"q": "front door", "limit": 5}).prepare()
>>> prepared.url
'https://example.com/search?q=front+door&limit=5'
```

### Methods and status codes

| Method | Used to |
|---|---|
| `GET` | read something |
| `POST` | send something (a message, a photo, a form) |

Every response has a **status code**:

| Code | Meaning |
|---|---|
| `200` | OK |
| `400` | Bad request (something you sent is wrong) |
| `401` | Unauthorized (wrong or missing key or token) |
| `403` | Forbidden (you are not allowed) |
| `404` | Not found |
| `429` | Too many requests (slow down) |
| `500` | The server has a problem |

`2xx` means success, `4xx` means **your** mistake, `5xx` means the **server's** problem.

### `requests`

| Call | Meaning |
|---|---|
| `requests.get(url, params={...}, timeout=10)` | a GET request |
| `requests.post(url, data={...}, files={...}, timeout=10)` | a POST request |
| `response.status_code` | the status number |
| `response.ok` | `True` for 2xx codes |
| `response.json()` | turns a JSON body into a Python dictionary |
| `response.text` | the body as text |

Two rules:

1. **Always set `timeout`.** Without it a stuck server can freeze your program forever.
2. Two kinds of failure are different. A server that answers with an **error status** (404, 401) does **not** raise an exception: you must check `response.ok` or the code. If you **cannot reach** the server at all (no internet, wrong name), `requests` raises an exception that is a `requests.RequestException`.

## Lab 10.1: Call a public API

`jsonplaceholder.typicode.com` is a free practice server that always returns the same fake data. Create `exercises/day10/api_demo.py`:

**`exercises/day10/api_demo.py`**

```python
import requests

url = "https://jsonplaceholder.typicode.com/todos/1"
response = requests.get(url, timeout=10)  # always give a timeout

print("status code:", response.status_code)
print("ok:", response.ok)
print("content type:", response.headers["Content-Type"])

data = response.json()  # JSON text -> Python dictionary
print("title:", data["title"])
print("completed:", data["completed"])
```

```text
$ python exercises/day10/api_demo.py
status code: 200
ok: True
content type: application/json; charset=utf-8
title: delectus aut autem
completed: False
```

(You need internet for this lab. If the site is down, the next lab still works for the error part.)

## Lab 10.2: See the two kinds of failure

**`exercises/day10/errors_demo.py`**

```python
import requests

# 1. The server answers, but with an error status: this is NOT an exception
response = requests.get("https://jsonplaceholder.typicode.com/todos/999999", timeout=10)
print("missing item:", response.status_code, "ok =", response.ok)

# 2. We cannot reach any server at all: this IS an exception.
#    Nothing listens on port 9 of your own computer, so the connection is refused at once.
try:
    requests.get("http://127.0.0.1:9/", timeout=5)
except requests.RequestException as error:
    print("no connection:", type(error).__name__)
```

```text
$ python exercises/day10/errors_demo.py
missing item: 404 ok = False
no connection: ConnectionError
```

The first request reached the server, which answered `404`: no exception, so we look at the status. The second never reached a server (nothing listens on that port of your own computer), so it raised an exception: we catch `requests.RequestException` and print its **type** only.

**Try:** turn off your Wi-Fi and run `api_demo.py`. What error do you see? Then wrap the call in `try/except requests.RequestException` to print a friendly message instead.

## Check yourself

1. What does the status code `401` mean? And `404`?
2. If `requests.get(...)` returns status `500`, is an exception raised?
3. Why do we use `timeout`?

<details><summary>Answers</summary>

1. `401`: you are not authorised (for example a wrong token). `404`: the thing you asked for does not exist.
2. No. The server answered, so `requests` is happy. You must check `response.ok` yourself.
3. Without a timeout the program could wait forever for a server that never answers.

</details>

---

# Hour 29: The Telegram Bot API

## Learn

Telegram lets you create **bots**: automatic accounts that your programs control through HTTP. A bot has a **token**, a long secret text like `123456789:ABCdef...`. Anyone who has the token can control your bot, so the token is a **password**.

The URL of every request is:

```text
https://api.telegram.org/bot<TOKEN>/<method>
```

The methods you need:

| Method | Does |
|---|---|
| `getMe` | tells you who the bot is (a good test that the token works) |
| `getUpdates` | lists the messages people sent to the bot (to find your chat id) |
| `sendMessage` | sends text to a chat |
| `sendPhoto` | sends a picture to a chat |

A **chat id** is the number that identifies one conversation (you, in a private chat). The bot can only send to a chat that has already started a conversation with it.

## Lab 10.3: Create your bot

Do these steps on your phone or on Telegram Desktop:

1. Search for **@BotFather** (it has a blue check mark) and press **Start**.
2. Send `/newbot`.
3. BotFather asks for a **name** (what people see, for example `Sokha Camera`). Type one.
4. BotFather asks for a **username**. It must be unique and end with `bot`, for example `sokha_camera_bot`. If it is taken, try another.
5. BotFather answers with a message that contains **"Use this token to access the HTTP API"** and your token. Copy the token. **Do not share it and do not take a screenshot of it.**
6. Open the link to your new bot (`t.me/<your username>`), press **Start**, and send the message `hello`. (A bot cannot write to you until you write to it first.)
7. Open your `.env` file in VS Code and paste the token:

```text
TELEGRAM_BOT_TOKEN=paste-your-token-here
TELEGRAM_CHAT_ID=
```

No spaces around `=`, no quotes needed.

## Lab 10.4: Find your chat id and send a message

The `getUpdates` method returns the messages sent to your bot. It looks like this (an example with made-up numbers):

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 100000001,
      "message": {
        "message_id": 1,
        "from": {"id": 987654321, "is_bot": false, "first_name": "Sokha"},
        "chat": {"id": 987654321, "first_name": "Sokha", "type": "private"},
        "text": "hello"
      }
    }
  ]
}
```

The chat id is at `result[0]["message"]["chat"]["id"]`. Read it from left to right: a list, then its first item (a dictionary), then `"message"`, then `"chat"`, then `"id"`. That is a nested JSON path, exactly like Day 3.

Copy these two helpers into your `tools` folder. They use your `load_env` from Day 4 and the `requests` library from hour 28.

**`tools/telegram_chat_id.py`**

```python
"""Find your Telegram chat id. First send any message to your bot in Telegram, then run:

    python -m tools.telegram_chat_id
"""
import requests

from intelligence import PROJECT_ROOT
from intelligence.config import load_env


def main():
    token = load_env(PROJECT_ROOT / ".env").get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Put TELEGRAM_BOT_TOKEN in the .env file first.")

    try:
        reply = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
    except requests.RequestException as error:
        # Print only the type: the message would contain the URL, and the URL contains the token.
        raise SystemExit(f"Could not reach Telegram: {type(error).__name__}")

    data = reply.json()
    if not data.get("ok"):
        raise SystemExit(f"Telegram refused the token: {data.get('description')} (status {reply.status_code})")

    chats = {}
    for update in data["result"]:
        message = update.get("message") or update.get("channel_post") or {}
        chat = message.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("first_name") or chat.get("title") or chat.get("username") or "?"

    if not chats:
        raise SystemExit("No messages found. Open your bot in Telegram, press Start, send 'hello', and run this again.")
    for chat_id, name in chats.items():
        print(f"chat id {chat_id}  ({name})")
    print("Copy the number into TELEGRAM_CHAT_ID in your .env file.")


if __name__ == "__main__":
    main()
```

**`tools/telegram_check.py`**

```python
"""Check your Telegram settings (token and chat id in .env).

    python -m tools.telegram_check                      who is my bot?
    python -m tools.telegram_check --send               also send a test message
    python -m tools.telegram_check --photo some.jpg     also send a picture
"""
import argparse

import requests

from intelligence import PROJECT_ROOT
from intelligence.config import load_env


def call(token, method, data=None, files=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        return requests.post(url, data=data, files=files, timeout=20)
    except requests.RequestException as error:
        # Print only the type: the message would contain the URL, and the URL contains the token.
        raise SystemExit(f"Could not reach Telegram: {type(error).__name__}")


def report(what, reply):
    try:
        data = reply.json()
    except ValueError:
        data = {}
    if data.get("ok"):
        print(f"{what}: sent")
    else:
        raise SystemExit(f"{what} failed: {data.get('description')} (status {reply.status_code})")


def main():
    ap = argparse.ArgumentParser(description="Check the Telegram settings in .env")
    ap.add_argument("--send", action="store_true", help="send a test message")
    ap.add_argument("--photo", help="send this picture too")
    args = ap.parse_args()

    env = load_env(PROJECT_ROOT / ".env")
    token, chat_id = env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("Put TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the .env file first.")

    reply = call(token, "getMe")
    info = reply.json()
    if not info.get("ok"):
        raise SystemExit(f"Telegram refused the token: {info.get('description')} (status {reply.status_code})")
    print("Bot found: @" + info["result"]["username"])

    if args.send:
        report("message", call(token, "sendMessage", data={"chat_id": chat_id, "text": "Hello from my Intelligence System!"}))
    if args.photo:
        with open(args.photo, "rb") as f:
            report("photo", call(token, "sendPhoto", data={"chat_id": chat_id, "caption": "Test photo"}, files={"photo": f}))


if __name__ == "__main__":
    main()
```

Notice three details that protect your token:

- The token is read from `.env`, never written in the code.
- It is never printed.
- When the network fails, the program prints only the **type** of the exception (`ConnectionError`). The full message of a `requests` exception contains the URL, and the URL contains your token!

Now use them:

```bash
python -m tools.telegram_chat_id
```

It prints something like `chat id 987654321  (Sokha)`. Put that number in `.env`:

```text
TELEGRAM_CHAT_ID=987654321
```

Check your bot, then send a test message:

```bash
python -m tools.telegram_check --send
```

You should see `Bot found: @your_bot_username` and `message: sent`, and the message **Hello from my Intelligence System!** should appear on your phone.

### What a wrong setting looks like

If the token is wrong (we use a fake one here), Telegram answers `401` and the helper tells you in one clear line:

```text
$ python -m tools.telegram_check --send
Telegram refused the token: Unauthorized (status 401)
```

| What you see | Cause | Fix |
|---|---|---|
| `Telegram refused the token: Unauthorized (status 401)` | wrong, incomplete or revoked token | copy the token again from BotFather; no spaces or quotes |
| `message failed: Bad Request: chat not found (status 400)` | wrong chat id, or you never pressed **Start** on your bot | press Start, send `hello`, run `tools.telegram_chat_id` again |
| `message failed: Forbidden: bot was blocked by the user (status 403)` | you blocked the bot | unblock it in Telegram |
| `message failed: Too Many Requests ... (status 429)` | you sent too many messages too fast | wait a few seconds. The project has a cooldown for this reason (Day 14) |
| `Could not reach Telegram: ConnectionError` | no internet, or Telegram is blocked on this network | check the connection; try a phone hotspot |

## Check yourself

1. What is the difference between the token and the chat id?
2. Why must you send `hello` to your bot before it can write to you?
3. Why does the helper print `type(error).__name__` and not the error message?

<details><summary>Answers</summary>

1. The token identifies and controls the **bot** (it is secret). The chat id identifies the **conversation** the bot sends to (it is not a secret, but it is private).
2. Telegram does not allow bots to start conversations. The bot can only answer chats that a person opened.
3. The error message contains the full URL, and the URL contains the token.

</details>

---

# Hour 30: Keeping secrets and sending photos

## Learn: secrets

You will meet three places where secrets can leak. Check them every time:

| Danger | What to do |
|---|---|
| **In your code** (`token = "1234:abc"`) | never. Read it from `.env` |
| **In git** (committed `.env`) | `.env` is in `.gitignore`. Before every commit run `git status` and make sure `.env` is not listed |
| **In output** (a `print`, an error message, a screenshot, a chat message to a friend) | never print it; catch exceptions and print only the type |

If a token leaks, **revoke it now**: in Telegram, talk to @BotFather, send `/revoke`, choose your bot, and put the **new** token in `.env`. The old one stops working at once.

**Environment variables** are another place for secrets. They belong to a running program and are read with `os.environ`. Servers and cloud services usually use them. Our project reads a `.env` file, but it also uses environment variables for settings (you saw `os.environ[...]` in the Windows camera setting on Day 8):

```pycon
>>> import os
>>> os.environ["DEMO_TOKEN"] = "abc123"
>>> os.environ["DEMO_TOKEN"]
'abc123'
>>> os.getenv("DEMO_TOKEN")
'abc123'
>>> os.getenv("NOT_SET")
>>> os.getenv("NOT_SET", "default")
'default'
```

`os.getenv(name)` gives `None` for a missing variable, while `os.environ[name]` raises a `KeyError`. Setting `os.environ[...]` changes only the running program, not your computer.

## Learn: sending a photo

`sendMessage` sends a **form**: values as `data={"chat_id": ..., "text": ...}`. `sendPhoto` must also upload the **file**. For that, open it in binary mode (`"rb"`) and pass it with `files={"photo": f}`; `requests` builds a "multipart" upload for you:

```python
with open("snapshot.jpg", "rb") as f:
    requests.post(url, data={"chat_id": chat_id, "caption": "Person at the door"},
                  files={"photo": f}, timeout=20)
```

Facts about photos: use JPEG (or PNG); the file can be up to 10 MB; the **caption** can be up to 1024 characters. This is the same call your alert code will use on Day 11.

## Lab 10.5: Send a photo to your phone

Use any picture, for example the overlay you made on Day 7 (`output/day07_overlay.jpg`), or a snapshot from Day 8:

```bash
python -m tools.telegram_check --photo output/day07_overlay.jpg
```

You should see `photo: sent`, and the picture appears in your Telegram chat with the caption "Test photo". You can send both with `--send --photo output/day07_overlay.jpg`.

**Before you commit today**, run `git status` and check that `.env` is **not** in the list.

## Checkpoint 2: NumPy, OpenCV, SQL and HTTP (20 minutes)

Closed book, no running code. One point per question: 15 points.

1. What is `np.zeros((3, 4)).shape`?
2. What does `np.array([1, 2, 3, 4])[1:3]` give?
3. What does `np.array([1, 2, 3]) * 2` give?
4. In which colour order does OpenCV store a pixel?
5. Write the slice that crops the box `(x1, y1, x2, y2)` out of an image called `image`.
6. What does `np.array([250], dtype=np.uint8) + 10` give? Why?
7. Which point of a person's box do we test against a zone, and why?
8. What does `cv2.pointPolygonTest(...)` return for a point outside the polygon?
9. For a **video file**, what does `ok == False` from `cap.read()` mean?
10. Which OpenCV call lets the video window draw itself and tells you a key was pressed?
11. Which SQL clause keeps only the rows that match a condition?
12. Write a query that counts the rows of table `events` whose `label` is `'person'`.
13. Why do we use `?` placeholders in SQL?
14. Which HTTP status code means the Telegram token is wrong?
15. Where is the Telegram token stored in our project, and which file stops it from being committed?

<details><summary>Answer key (instructor)</summary>

Code answers computed by Python:

```pycon
>>> import numpy as np
>>> np.zeros((3, 4)).shape
(3, 4)
>>> np.array([1, 2, 3, 4])[1:3]
array([2, 3])
>>> np.array([1, 2, 3]) * 2
array([2, 4, 6])
>>> np.array([250], dtype=np.uint8) + 10
array([4], dtype=uint8)
```

The other answers:

4. Blue, green, red (BGR).
5. `image[y1:y2, x1:x2]` (rows, which are y, come first).
6. `array([4], dtype=uint8)`. A `uint8` holds 0 to 255, so 260 wraps around to 4.
7. The bottom centre, `((x1 + x2) / 2, y2)`: where the feet touch the ground. The box centre can look inside the zone for a person who is standing behind it.
8. `-1.0`.
9. The video has ended.
10. `cv2.waitKey(...)`.
11. `WHERE`.
12. `SELECT COUNT(*) FROM events WHERE label = 'person'`.
13. To stop SQL injection: the values are passed separately and can never be read as SQL.
14. `401`.
15. In the `.env` file. `.gitignore` stops it from being committed.

**Scoring:** 13-15 excellent, 10-12 good, 7-9 revise Days 6-9 with a partner, below 7 meet the student before Day 11. Two thirds of the class should be at 10 or above before you start Week 3. If they are not, spend the first 30 minutes of Day 11 on the weakest topic.

</details>

---

# Day 10 wrap-up

## Checklist

- [ ] You have a bot, a token and a chat id in `.env`.
- [ ] `python -m tools.telegram_check --send` shows **message: sent** and the message arrives on your phone.
- [ ] `python -m tools.telegram_check --photo output/day07_overlay.jpg` delivers a photo.
- [ ] `git status` does **not** list `.env`.
- [ ] You finished Checkpoint 2.
- [ ] You committed (`git commit -m "Day 10: telegram tools"`).

## Your project folder today

```text
my-intelligence-system/
├── .env                        <- now with your REAL token and chat id (never commit)
├── tools/
│   ├── run_sql.py
│   ├── seed_history.py
│   ├── plot_hours.py
│   ├── telegram_chat_id.py     <- new
│   └── telegram_check.py       <- new
└── exercises/day10/
    ├── api_demo.py
    └── errors_demo.py
```

Solutions are in [`solutions/day10/`](solutions/day10/): the exercise files directly in the folder, and the project files in [`project/`](solutions/day10/project/).

## Instructor notes

- **Prepare before class:** every student needs a Telegram account and the app on a phone or computer. In countries where Telegram is slow or blocked, test it on the classroom network the day before. A phone hotspot is the fallback.
- **BotFather usernames** are global: if `sokha_camera_bot` is taken, students should add digits or their initials.
- **The token is a password.** If a student shows it on the projector or pastes it into a chat, have them `/revoke` it immediately and use the moment to teach what a leak means.
- **"chat not found" (400)** is the most common problem: the student did not press Start on **their own bot** (not on BotFather).
- **Shared Wi-Fi can rate-limit** Telegram or the practice API. If the API lab fails for many students, demonstrate it on the projector and move on.
- **Group chats:** a group can receive alerts too (add the bot to the group, send a message in the group, then use `getUpdates`; group chat ids are negative numbers). Keep it as an optional extension.
- **If you are behind:** the order of importance is: bot created, token and chat id in `.env`, one message received. Photos can be done in 3 minutes after that.
- **Fast finishers:** send a message with a location (`sendLocation`), or read the Bot API documentation page for `sendPhoto` and find one more parameter (for example `disable_notification`) and use it.

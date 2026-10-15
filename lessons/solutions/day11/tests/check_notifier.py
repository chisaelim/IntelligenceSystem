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

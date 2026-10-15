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

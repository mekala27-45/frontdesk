"""Standard-library signed cron client. Prints no secrets or payloads."""

import hashlib
import hmac
import os
import secrets
import time
import urllib.request

if __name__ == "__main__":
    timestamp = str(int(time.time()))
    nonce = secrets.token_hex(16)
    signature = hmac.new(
        os.environ["REMINDER_SECRET"].encode(), (timestamp + "." + nonce).encode(), hashlib.sha256
    ).hexdigest()
    request = urllib.request.Request(
        os.environ["FRONTDESK_API_URL"].rstrip("/") + "/internal/reminders",
        data=b"",
        method="POST",
        headers={"X-Timestamp": timestamp, "X-Nonce": nonce, "X-Signature": signature},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            raise SystemExit("Reminder dispatch failed")
        print("Reminder endpoint completed")

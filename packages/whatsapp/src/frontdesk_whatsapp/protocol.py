import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any
from frontdesk_core.contracts import now

def signature(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

def verify(body: bytes, supplied: str, secret: str) -> bool:
    return bool(secret) and hmac.compare_digest(signature(body, secret), supplied)

def can_send_free_form(last_inbound_at: datetime, at: datetime | None = None) -> bool:
    elapsed = (at or now()) - last_inbound_at
    return timedelta(0) <= elapsed < timedelta(hours=24)

def text_message(to: str, body: str) -> dict[str, Any]:
    if chr(0x2014) in body:
        raise ValueError("Forbidden punctuation")
    return {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}

def template_message(to: str) -> dict[str, Any]:
    return {"messaging_product": "whatsapp", "to": to, "type": "template", "template": {"name": "hello_world", "language": {"code": "en_US"}}}

def list_message(to: str, title: str, rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows or len(rows) > 10:
        raise ValueError("Lists require one through ten rows")
    return {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {"type": "list", "body": {"text": title}, "action": {"button": "Choose an option", "sections": [{"title": "Available options", "rows": rows}]}}}

def buttons_message(to: str, body: str, buttons: list[tuple[str, str]]) -> dict[str, Any]:
    if not 1 <= len(buttons) <= 3:
        raise ValueError("Buttons require one through three options")
    return {"messaging_product": "whatsapp", "to": to, "type": "interactive", "interactive": {"type": "button", "body": {"text": body}, "action": {"buttons": [{"type": "reply", "reply": {"id": key, "title": label}} for key, label in buttons]}}}


from typing import Any, Protocol

import httpx
from frontdesk_core.config import Settings
from frontdesk_core.logging import log
from frontdesk_core.models import Outbox
from sqlalchemy import Engine
from sqlmodel import Session, select


class WhatsAppTransport(Protocol):
    def send(self, payload: dict[str, Any], phone_id: str) -> str: ...


class DevTransport:
    def send(self, payload: dict[str, Any], phone_id: str) -> str:
        # Complete generated payload is available in the durable ops outbox.
        # Logs deliberately exclude payloads and raw recipient identifiers.
        log.info("dev_delivery", kind=payload["type"], phone=payload["to"])
        return "dev:" + phone_id


class MetaTransport:
    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.Client(timeout=15)

    def send(self, payload: dict[str, Any], phone_id: str) -> str:
        response = self.client.post(
            f"https://graph.facebook.com/{self.settings.meta_graph_version}/{phone_id}/messages",
            headers={"Authorization": "Bearer " + self.settings.meta_token},
            json=payload,
        )
        response.raise_for_status()
        return str(response.json()["messages"][0]["id"])


def dispatch(db: Engine, transport: WhatsAppTransport, clinic: str, phone_id: str) -> int:
    sent = 0
    while True:
        with Session(db) as session:
            item = session.exec(
                select(Outbox)
                .where(Outbox.clinic_id == clinic, Outbox.status == "pending")
                .with_for_update(skip_locked=True)
            ).first()
            if item is None:
                break
            item.status = "sending"
            session.add(item)
            session.commit()
            item_id, payload = item.id, item.payload
        # Graph does not promise an idempotency key. Never resend ambiguous sends.
        try:
            provider_ref = transport.send(payload, phone_id)
            status = "sent"
            sent += 1
        except Exception:
            provider_ref, status = None, "unknown"
        with Session(db) as session:
            item = session.exec(
                select(Outbox).where(Outbox.id == item_id, Outbox.clinic_id == clinic)
            ).one()
            item.status, item.provider_ref = status, provider_ref
            session.add(item)
            session.commit()
    return sent

import json
from datetime import timedelta

import httpx
import pytest
from conftest import evidence
from frontdesk_api.app import create_app
from frontdesk_core.contracts import now, uuid7
from frontdesk_core.models import Booking, Conversation, Escalation, Message, Outbox
from frontdesk_whatsapp.protocol import (
    buttons_message,
    can_send_free_form,
    list_message,
    signature,
    template_message,
)
from frontdesk_whatsapp.transport import DevTransport
from sqlmodel import Session, select


def payload(phone, body, owner="15550001111", wamid=None, kind="text"):
    message = {
        "from": owner,
        "id": wamid or uuid7(),
        "timestamp": str(int(now().timestamp())),
        "type": kind,
    }
    if kind == "text":
        message["text"] = {"body": body}
    else:
        message["interactive"] = {
            "type": "list_reply",
            "list_reply": {"id": body, "title": "Choice"},
        }
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "demo-account",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": phone},
                            "messages": [message],
                        },
                    }
                ],
            }
        ],
    }


async def send(client, phone, body, owner="15550001111", wamid=None, kind="text"):
    raw = json.dumps(payload(phone, body, owner, wamid, kind)).encode()
    return await client.post(
        "/webhooks/whatsapp",
        content=raw,
        headers={"X-Hub-Signature-256": signature(raw, "local-meta-secret")},
    )


class CountingTransport(DevTransport):
    def __init__(self):
        self.calls = []

    def send(self, payload, phone_id):
        self.calls.append(payload)
        return super().send(payload, phone_id)


async def test_webhook_replay_and_restart(db, clinic):
    c, _, services, slots, _ = clinic
    transport = CountingTransport()
    app = create_app(db=db, transport=transport)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await send(client, c.whatsapp_phone_number_id, services[0].name)
        result = response.json()["results"][0]
        choice = result["reply"]["interactive"]["action"]["sections"][0]["rows"][0]["id"]
        await send(client, c.whatsapp_phone_number_id, choice, kind="interactive")
    # Recreate the application, transport and every request object.
    restarted = create_app(db=db, transport=transport)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=restarted), base_url="http://test"
    ) as client:
        wamid = uuid7()
        first = await send(client, c.whatsapp_phone_number_id, "confirm", wamid=wamid)
        before = len(transport.calls)
        replay = await send(client, c.whatsapp_phone_number_id, "confirm", wamid=wamid)
        assert replay.status_code == 200 and replay.json()["results"][0]["duplicate"]
        assert len(transport.calls) == before
        assert first.json()["results"][0]["calls"][0]["name"] == "book_slot"
        assert first.json()["results"][0]["calls"][0]["result"]["ok"]
    with Session(db) as session:
        bookings = session.exec(select(Booking).where(Booking.clinic_id == c.id)).all()
        messages = session.exec(
            select(Message).where(Message.clinic_id == c.id, Message.wamid == wamid)
        ).all()
        assert len(bookings) == len(messages) == 1
    evidence(
        db,
        "idempotency",
        {
            "deliveries": 2,
            "booking_rows": len(bookings),
            "clinic_id": c.id,
            "wamid": wamid,
            "inbound_rows": len(messages),
            "additional_outbound_on_retry": len(transport.calls) - before,
            "restart_resumed": True,
        },
    )


async def test_signature_rejects_before_parse(db, clinic):
    c, *_ = clinic
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(db=db)), base_url="http://test"
    ) as client:
        raw = json.dumps(payload(c.whatsapp_phone_number_id, "hello")).encode()
        response = await client.post(
            "/webhooks/whatsapp",
            content=raw + b"x",
            headers={"X-Hub-Signature-256": signature(raw, "local-meta-secret")},
        )
        assert response.status_code == 403
        invalid = await client.post(
            "/webhooks/whatsapp",
            content=b"invalid",
            headers={"X-Hub-Signature-256": signature(b"invalid", "local-meta-secret")},
        )
        assert invalid.status_code == 400
        assert (
            await client.get(
                "/webhooks/whatsapp",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "local-verify-token",
                    "hub.challenge": "123",
                },
            )
        ).text == "123"
        assert (await client.get("/webhooks/whatsapp")).status_code == 403
        assert (await client.get("/health")).status_code == 200
        large = b"x" * 17000
        assert (await client.post("/webhooks/whatsapp", content=large)).status_code == 413


@pytest.mark.parametrize(
    "seconds,expected", [(86399, True), (86400, False), (86401, False), (-1, False), (0, True)]
)
def test_session_boundary(seconds, expected):
    at = now()
    assert can_send_free_form(at - timedelta(seconds=seconds), at) == expected


async def test_emergency_first_and_no_raw_persistence(db, clinic):
    c, _, _, slots, convo = clinic
    with Session(db) as session:
        row = session.get(Conversation, convo.id)
        row.status = "escalated"
        row.state = {"pending_slot": slots[0].id}
        session.add(row)
        session.commit()
    raw = "chest pain, secret-clinical-sentinel"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(db=db)), base_url="http://test"
    ) as client:
        result = (await send(client, c.whatsapp_phone_number_id, raw)).json()["results"][0]
        assert [c["name"] for c in result["calls"]] == ["escalate_to_human"]
        assert result["calls"][0]["arguments"]["category"] == "emergency"
    with Session(db) as session:
        for model in [Conversation, Message, Outbox, Escalation]:
            rows = session.exec(select(model).where(model.clinic_id == c.id)).all()
            assert "secret-clinical-sentinel" not in str([r.model_dump() for r in rows])
        assert not session.exec(select(Booking).where(Booking.clinic_id == c.id)).all()


async def test_simulator_identity_and_ops_auth(db):
    from conftest import make_clinic

    with Session(db) as session:
        from frontdesk_core.models import Clinic

        existing = session.exec(
            select(Clinic).where(Clinic.whatsapp_phone_number_id == "demo-phone")
        ).first()
        if existing is None:
            make_clinic(session, "demo-phone")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(db=db)), base_url="http://test"
    ) as client:
        identity = (await client.post("/internal/simulator/session")).json()
        headers = {"Authorization": "Bearer " + identity["token"]}
        good = await client.post(
            "/internal/simulator",
            json=payload("demo-phone", "hello", identity["wa_id"]),
            headers=headers,
        )
        assert good.status_code == 200
        assert (
            await client.post(
                "/internal/simulator",
                json=payload("demo-phone", "hello", "15550001111"),
                headers=headers,
            )
        ).status_code == 403
        assert (await client.post("/internal/simulator", json={})).status_code == 401
        assert (await client.get("/ops")).status_code == 401
        data = (
            await client.get("/ops", headers={"Authorization": "Bearer local-ops-token"})
        ).json()
        cid = good.json()["results"][0]["conversation_id"]
        replay = await client.get(
            "/ops/replay/" + cid,
            params={"clinic_id": data["clinic"]["id"]},
            headers={"Authorization": "Bearer local-ops-token"},
        )
        assert replay.status_code == 200 and replay.json()["messages"]
        assert (
            await client.get(
                "/ops/replay/" + cid,
                params={"clinic_id": "foreign"},
                headers={"Authorization": "Bearer local-ops-token"},
            )
        ).status_code == 403


def test_interactive_contract_limits():
    assert template_message("15550001111")["type"] == "template"
    with pytest.raises(ValueError):
        buttons_message("1", "test", [])
    with pytest.raises(ValueError):
        list_message("1", "test", [])
    from frontdesk_whatsapp.protocol import text_message

    with pytest.raises(ValueError):
        text_message("1", chr(0x2014))

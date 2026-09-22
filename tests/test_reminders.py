from datetime import timedelta

import httpx
from frontdesk_api.app import create_app
from frontdesk_api.reminders import signed
from frontdesk_core.contracts import now, uuid7
from frontdesk_core.models import ReminderAttempt, ReminderRun, Slot
from frontdesk_scheduling.engine import claim
from sqlmodel import Session, select


async def test_reminder_step_actually_ran(db, clinic):
    c, _, _, slots, _ = clinic
    with Session(db) as session:
        slot = session.get(Slot, slots[0].id)
        slot.starts_at = now() + timedelta(hours=1, minutes=30)
        slot.ends_at = slot.starts_at + timedelta(minutes=30)
        session.add(slot)
        session.commit()
        claim(session, c.id, "15550001111", slot.id)
        session.commit()

    def headers():
        timestamp = str(int(now().timestamp()))
        nonce = uuid7()
        return {
            "X-Timestamp": timestamp,
            "X-Nonce": nonce,
            "X-Signature": signed(timestamp, nonce, "local-reminder-secret"),
        }

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(db=db)), base_url="http://test"
    ) as client:
        auth = headers()
        response = await client.post("/internal/reminders", headers=auth)
        assert response.status_code == 200
        assert (await client.post("/internal/reminders", headers=auth)).status_code == 403
        assert (await client.post("/internal/reminders", headers=headers())).status_code == 200
        assert (await client.post("/internal/reminders")).status_code == 403
    with Session(db) as session:
        run = session.exec(select(ReminderRun).where(ReminderRun.nonce == auth["X-Nonce"])).one()
        assert run.query_executed is True
        attempts = session.exec(
            select(ReminderAttempt).where(ReminderAttempt.clinic_id == c.id)
        ).all()
        assert len(attempts) == 1 and attempts[0].hours_before == 2


async def test_empty_due_query_is_still_a_run(db):
    timestamp = str(int(now().timestamp()))
    nonce = uuid7()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(db=db)), base_url="http://test"
    ) as client:
        assert (
            await client.post(
                "/internal/reminders",
                headers={
                    "X-Timestamp": timestamp,
                    "X-Nonce": nonce,
                    "X-Signature": signed(timestamp, nonce, "local-reminder-secret"),
                },
            )
        ).status_code == 200
    with Session(db) as session:
        assert (
            session.exec(select(ReminderRun).where(ReminderRun.nonce == nonce)).one().query_executed
        )

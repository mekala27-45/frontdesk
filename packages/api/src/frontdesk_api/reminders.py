import hashlib
import hmac
from datetime import timedelta
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from frontdesk_core.contracts import now
from frontdesk_core.models import Booking, Conversation, Outbox, ReminderAttempt, ReminderRun, Slot
from frontdesk_whatsapp.protocol import template_message

def signed(timestamp: str, nonce: str, secret: str) -> str:
    return hmac.new(secret.encode(), (timestamp + "." + nonce).encode(), hashlib.sha256).hexdigest()

def run(db: Engine, timestamp: str, nonce: str, supplied: str, secret: str) -> dict[str, int]:
    if not nonce or len(nonce) > 80 or abs(now().timestamp() - float(timestamp)) > 300 or not hmac.compare_digest(signed(timestamp, nonce, secret), supplied):
        raise PermissionError("Invalid reminder signature")
    with Session(db) as session:
        attempt = ReminderRun(nonce=nonce)
        session.add(attempt)
        try:
            session.flush()
        except IntegrityError as exc:
            raise PermissionError("Reminder replay") from exc
        due = session.exec(select(Booking, Slot).join(Slot, Booking.slot_id == Slot.id).where(Booking.status == "confirmed", Slot.clinic_id == Booking.clinic_id, Slot.starts_at > now(), Slot.starts_at <= now() + timedelta(hours=24))).all()
        attempt.query_executed = True
        attempt.candidates = len(due)
        queued = 0
        for booking, slot in due:
            hours = (slot.starts_at - now()).total_seconds() / 3600
            for threshold in (24, 2):
                if hours > threshold or (threshold == 24 and hours <= 2):
                    continue
                existing = session.exec(select(ReminderAttempt).where(ReminderAttempt.clinic_id == booking.clinic_id, ReminderAttempt.booking_id == booking.id, ReminderAttempt.hours_before == threshold)).first()
                if existing:
                    continue
                conversation = session.exec(select(Conversation).where(Conversation.clinic_id == booking.clinic_id, Conversation.wa_id == booking.patient_wa_id)).first()
                if conversation is None:
                    continue
                row = ReminderAttempt(clinic_id=booking.clinic_id, booking_id=booking.id, hours_before=threshold)
                session.add(row)
                session.flush()
                session.add(Outbox(clinic_id=booking.clinic_id, conversation_id=conversation.id, message_id="reminder:" + row.id, payload=template_message(booking.patient_wa_id)))
                queued += 1
        session.add(attempt)
        session.commit()
        return {"candidates": len(due), "queued": queued}


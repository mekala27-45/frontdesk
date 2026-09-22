from datetime import timedelta
from sqlmodel import Session, select
from sqlalchemy import text
from frontdesk_core.contracts import now
from frontdesk_core.models import Booking, CalendarJob, Clinic, Provider, Slot

class Denied(ValueError):
    pass

class Unavailable(ValueError):
    pass

def scoped_slot(session: Session, clinic: str, slot_id: str) -> Slot:
    slot = session.exec(select(Slot).where(Slot.id == slot_id, Slot.clinic_id == clinic)).first()
    if slot is None:
        raise Denied("Resource unavailable in caller scope")
    return slot

def own_booking(session: Session, clinic: str, owner: str, booking_id: str) -> Booking:
    booking = session.exec(select(Booking).where(Booking.id == booking_id, Booking.clinic_id == clinic, Booking.patient_wa_id == owner).with_for_update()).first()
    if booking is None:
        raise Denied("Resource unavailable in caller scope")
    return booking

def claim(session: Session, clinic: str, owner: str, slot_id: str, booking: Booking | None = None) -> Booking:
    candidate = scoped_slot(session, clinic, slot_id)
    provider_ids = {candidate.provider_id}
    old: Slot | None = None
    if booking:
        old = scoped_slot(session, clinic, booking.slot_id)
        provider_ids.add(old.provider_id)
    # Lock every affected provider in stable order; covers overlapping services.
    for provider_id in sorted(provider_ids):
        provider = session.exec(select(Provider).where(Provider.id == provider_id, Provider.clinic_id == clinic).with_for_update(skip_locked=True)).first()
        if provider is None:
            raise Unavailable("No longer available")
    slot = session.exec(select(Slot).where(Slot.id == slot_id, Slot.clinic_id == clinic, Slot.status == "open").with_for_update(skip_locked=True).execution_options(populate_existing=True)).first()
    if slot is None:
        raise Unavailable("No longer available")
    rules = session.exec(select(Clinic).where(Clinic.id == clinic)).one()
    if slot.starts_at < now() + timedelta(minutes=rules.min_notice_minutes) or slot.starts_at > now() + timedelta(days=rules.booking_horizon_days):
        raise Unavailable("Outside booking window")
    overlap = session.exec(select(Slot).where(Slot.clinic_id == clinic, Slot.provider_id == slot.provider_id, Slot.status.in_(["booked", "blocked"]), Slot.starts_at < slot.ends_at, Slot.ends_at > slot.starts_at, Slot.id != (old.id if old else ""))).first()
    if overlap:
        raise Unavailable("No longer available")
    if booking is None:
        booking = Booking(clinic_id=clinic, slot_id=slot.id, patient_wa_id=owner, service_id=slot.service_id)
    else:
        if booking.status != "confirmed":
            raise Unavailable("Booking is not active")
        assert old is not None
        old.status, old.version = "open", old.version + 1
        session.add(old)
        booking.slot_id, booking.service_id = slot.id, slot.service_id
    slot.status, slot.version = "booked", slot.version + 1
    session.add(slot)
    session.add(booking)
    session.flush()
    queue_calendar(session, booking)
    return booking

def queue_calendar(session: Session, booking: Booking) -> None:
    job = session.exec(select(CalendarJob).where(CalendarJob.clinic_id == booking.clinic_id, CalendarJob.booking_id == booking.id)).first()
    if job:
        job.status = "pending"
    else:
        job = CalendarJob(clinic_id=booking.clinic_id, booking_id=booking.id)
    session.add(job)

def cancel(session: Session, clinic: str, owner: str, booking_id: str) -> Booking:
    booking = own_booking(session, clinic, owner, booking_id)
    slot = scoped_slot(session, clinic, booking.slot_id)
    session.exec(select(Provider).where(Provider.id == slot.provider_id, Provider.clinic_id == clinic).with_for_update()).one()
    if booking.status == "confirmed":
        slot.status, slot.version = "open", slot.version + 1
        booking.status, booking.cancelled_at = "cancelled", now()
        session.add(slot)
        session.add(booking)
        queue_calendar(session, booking)
    return booking

def lock_conversation(session: Session, clinic: str, owner: str) -> None:
    session.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"), {"key": clinic + ":" + owner})


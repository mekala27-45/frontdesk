from typing import Any, Protocol
from sqlalchemy import Engine
from sqlmodel import Session, select
from frontdesk_core.config import Settings
from frontdesk_core.models import Booking, CalendarJob, Slot
from frontdesk_core.logging import log

class CalendarAdapter(Protocol):
    def sync(self, booking: Booking, slot: Slot) -> str: ...

class NullCalendarAdapter:
    def sync(self, booking: Booking, slot: Slot) -> str:
        log.info("calendar_disabled", id=booking.id, status=booking.status)
        return "null:" + booking.id

class GoogleCalendarAdapter:
    def __init__(self, settings: Settings, service: Any = None) -> None:
        self.calendar_id = settings.google_calendar_id
        if service is None:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            credentials = service_account.Credentials.from_service_account_file(settings.google_application_credentials, scopes=["https://www.googleapis.com/auth/calendar.events"])
            service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        self.service = service

    def sync(self, booking: Booking, slot: Slot) -> str:
        from googleapiclient.errors import HttpError
        event_id = booking.id.replace("-", "")
        events = self.service.events()
        if booking.status != "confirmed":
            try:
                events.delete(calendarId=self.calendar_id, eventId=event_id).execute()
            except HttpError as exc:
                if exc.resp.status not in (404, 410):
                    raise
            return event_id
        body = {"id": event_id, "summary": "Fictional clinic appointment", "start": {"dateTime": slot.starts_at.isoformat()}, "end": {"dateTime": slot.ends_at.isoformat()}, "description": "Demo logistics only. Reference " + booking.id}
        try:
            events.insert(calendarId=self.calendar_id, body=body).execute()
        except HttpError as exc:
            if exc.resp.status != 409:
                raise
            events.update(calendarId=self.calendar_id, eventId=event_id, body=body).execute()
        return event_id

def sync_pending(db: Engine, adapter: CalendarAdapter) -> int:
    count = 0
    with Session(db) as session:
        jobs = session.exec(select(CalendarJob).where(CalendarJob.status == "pending").with_for_update(skip_locked=True)).all()
        for job in jobs:
            booking = session.exec(select(Booking).where(Booking.id == job.booking_id, Booking.clinic_id == job.clinic_id)).one()
            slot = session.exec(select(Slot).where(Slot.id == booking.slot_id, Slot.clinic_id == job.clinic_id)).one()
            try:
                booking.calendar_event_ref = adapter.sync(booking, slot)
                job.status = "synced"
                count += 1
            except Exception:
                log.warning("calendar_retry_pending", id=job.id)
            session.add(booking)
            session.add(job)
        session.commit()
    return count


from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from sqlmodel import Session, select
from frontdesk_core.contracts import now
from frontdesk_core.models import Clinic, Provider, ProviderService, Service, Slot

def intervals(day: date, timezone: str, opening: int, closing: int, minutes: int) -> list[tuple[datetime, datetime]]:
    if minutes <= 0 or not 0 <= opening < closing <= 24:
        raise ValueError("Invalid business interval")
    zone = ZoneInfo(timezone)
    start = datetime.combine(day, time.min, tzinfo=zone) + timedelta(hours=opening)
    end = datetime.combine(day, time.min, tzinfo=zone) + timedelta(hours=closing)
    cursor, limit = start.astimezone(UTC), end.astimezone(UTC)
    result = []
    while cursor + timedelta(minutes=minutes) <= limit:
        nxt = cursor + timedelta(minutes=minutes)
        result.append((cursor, nxt))
        cursor = nxt
    return result

def generate(session: Session, clinic_id: str, at: datetime | None = None) -> int:
    at = at or now()
    clinic = session.exec(select(Clinic).where(Clinic.id == clinic_id)).one()
    count = 0
    for provider in session.exec(select(Provider).where(Provider.clinic_id == clinic_id)).all():
        links = session.exec(select(ProviderService).where(ProviderService.clinic_id == clinic_id, ProviderService.provider_id == provider.id)).all()
        for link in links:
            service = session.exec(select(Service).where(Service.id == link.service_id, Service.clinic_id == clinic_id)).one()
            for offset in range(clinic.booking_horizon_days):
                day = at.astimezone(ZoneInfo(clinic.timezone)).date() + timedelta(days=offset)
                hours = (provider.working_hours_override or clinic.business_hours).get(str(day.weekday()))
                if not hours:
                    continue
                for start, end in intervals(day, clinic.timezone, hours[0], hours[1], service.duration_minutes + service.buffer_minutes):
                    if start < at + timedelta(minutes=clinic.min_notice_minutes):
                        continue
                    existing = session.exec(select(Slot).where(Slot.clinic_id == clinic_id, Slot.provider_id == provider.id, Slot.service_id == service.id, Slot.starts_at == start)).first()
                    if existing is None:
                        session.add(Slot(clinic_id=clinic_id, provider_id=provider.id, service_id=service.id, starts_at=start, ends_at=end))
                        count += 1
    session.flush()
    return count


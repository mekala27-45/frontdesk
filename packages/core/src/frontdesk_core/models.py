from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, Index, JSON, UniqueConstraint, text
from sqlmodel import Field, SQLModel
from frontdesk_core.contracts import now, uuid7

def stamp() -> Any:
    return Field(default_factory=now, sa_column=Column(DateTime(timezone=True), nullable=False))

class Clinic(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    name: str
    timezone: str = "America/New_York"
    business_hours: dict[str, list[int]] = Field(default_factory=lambda: {str(i): [9, 17] for i in range(5)}, sa_column=Column(JSON))
    booking_horizon_days: int = 14
    min_notice_minutes: int = 60
    whatsapp_phone_number_id: str = Field(unique=True)

class Provider(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    name: str
    working_hours_override: dict[str, list[int]] = Field(default_factory=dict, sa_column=Column(JSON))

class Service(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    name: str
    duration_minutes: int = 30
    buffer_minutes: int = 0

class ProviderService(SQLModel, table=True):
    provider_id: str = Field(foreign_key="provider.id", primary_key=True)
    service_id: str = Field(foreign_key="service.id", primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)

class Slot(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("clinic_id", "provider_id", "service_id", "starts_at"),)
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    provider_id: str = Field(foreign_key="provider.id", index=True)
    service_id: str = Field(foreign_key="service.id", index=True)
    starts_at: datetime = stamp()
    ends_at: datetime = stamp()
    status: str = "open"
    version: int = 0

class Booking(SQLModel, table=True):
    __table_args__ = (Index("one_confirmed_booking_per_slot", "slot_id", unique=True, postgresql_where=text("status = 'confirmed'")),)
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    slot_id: str = Field(foreign_key="slot.id", index=True)
    patient_name: str = "Demo visitor"
    patient_wa_id: str = Field(index=True)
    service_id: str = Field(foreign_key="service.id")
    status: str = "confirmed"
    calendar_event_ref: str | None = None
    created_at: datetime = stamp()
    cancelled_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))

class Conversation(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("clinic_id", "wa_id"),)
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    wa_id: str
    state: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    last_inbound_at: datetime = stamp()
    last_message_id: str = ""
    status: str = "active"

class Message(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    direction: str
    wamid: str = Field(unique=True)
    content_summary: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = stamp()

class Escalation(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    reason: str
    opened_at: datetime = stamp()
    resolved_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    resolved_by: str | None = None

class Outbox(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    conversation_id: str = Field(foreign_key="conversation.id")
    message_id: str = Field(unique=True)
    payload: dict[str, Any] = Field(sa_column=Column(JSON))
    status: str = "pending"
    provider_ref: str | None = None
    created_at: datetime = stamp()

class CalendarJob(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    booking_id: str = Field(foreign_key="booking.id", unique=True)
    status: str = "pending"

class ReminderAttempt(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("booking_id", "hours_before"),)
    id: str = Field(default_factory=uuid7, primary_key=True)
    clinic_id: str = Field(foreign_key="clinic.id", index=True)
    booking_id: str = Field(foreign_key="booking.id")
    hours_before: int
    status: str = "pending"
    created_at: datetime = stamp()

class ReminderRun(SQLModel, table=True):
    id: str = Field(default_factory=uuid7, primary_key=True)
    nonce: str = Field(unique=True)
    query_executed: bool = False
    candidates: int = 0
    created_at: datetime = stamp()

class Evidence(SQLModel, table=True):
    name: str = Field(primary_key=True)
    value: dict[str, Any] = Field(sa_column=Column(JSON))


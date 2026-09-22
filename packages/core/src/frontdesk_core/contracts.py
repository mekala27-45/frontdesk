import secrets
import threading
import time
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

_lock = threading.Lock()
_last = 0

def uuid7() -> str:
    global _last
    with _lock:
        bits = secrets.randbits(74)
        value = (time.time_ns() // 1_000_000 << 80) | (7 << 76) | ((bits >> 62) << 64) | (2 << 62) | (bits & ((1 << 62) - 1))
        _last = max(value, _last + 1)
        return str(UUID(int=_last))

def now() -> datetime:
    return datetime.now(UTC)

Category = Literal["medical_question", "prescription_question", "emergency", "pricing_or_insurance_detail", "other_patient_data", "unrelated"]
ToolName = Literal["check_availability", "book_slot", "reschedule_booking", "cancel_booking", "get_my_bookings", "escalate_to_human", "refuse_out_of_scope"]

class ToolArgs(StrictModel):
    slot_id: str | None = None
    booking_id: str | None = None
    service_id: str | None = None
    provider_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    patient_wa_id: str | None = None
    patient_name: Literal["Demo visitor"] = "Demo visitor"
    category: Category = "unrelated"

class ToolResult(StrictModel):
    ok: bool
    code: str
    ids: list[str] = Field(default_factory=list)

class ToolCall(StrictModel):
    name: ToolName
    arguments: ToolArgs
    result: ToolResult


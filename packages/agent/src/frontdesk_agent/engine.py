import re
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo
from sqlalchemy import Engine
from sqlmodel import Session, select
from frontdesk_core.contracts import ToolArgs, ToolCall, ToolName, now
from frontdesk_core.models import Clinic, Conversation, Message, Outbox, Service, Slot
from frontdesk_scheduling.engine import Denied, lock_conversation
from frontdesk_agent.safety import REFUSALS, classify_safety
from frontdesk_agent.tools import invoke
from frontdesk_whatsapp.protocol import buttons_message, can_send_free_form, list_message, template_message, text_message

def respond(session: Session, clinic: Clinic, convo: Conversation, body: str) -> tuple[dict[str, Any], list[ToolCall], str]:
    owner, state = convo.wa_id, dict(convo.state)
    calls: list[ToolCall] = []
    def call(name: ToolName, args: ToolArgs | None = None) -> ToolCall:
        result = invoke(session, clinic.id, owner, convo.id, name, args or ToolArgs())
        calls.append(result)
        return result
    category = classify_safety(body)
    if category:
        # First action, including when already escalated or partially booked.
        call("escalate_to_human" if category == "emergency" else "refuse_out_of_scope", ToolArgs(category=category))
        convo.state = {}
        return text_message(owner, REFUSALS[category]), calls, category
    if convo.status == "escalated":
        return text_message(owner, "Your conversation is with the front desk. Please wait for their reply."), calls, "handoff_wait"
    normalized = body.strip().lower()
    if normalized in {"human", "talk to a person", "person", "help from a person"}:
        call("escalate_to_human")
        return text_message(owner, "I have sent your request to the front desk."), calls, "handoff"
    services = session.exec(select(Service).where(Service.clinic_id == clinic.id)).all()
    if normalized in {"no", "back", "start over"}:
        state = {}
    if normalized in {"yes", "confirm"} and state.get("pending_slot"):
        name: ToolName = "reschedule_booking" if state.get("booking_id") else "book_slot"
        result = call(name, ToolArgs(slot_id=state["pending_slot"], booking_id=state.get("booking_id")))
        convo.state = {}
        reply = "Your appointment is confirmed." if result.result.ok else "That time is no longer available. Please choose another."
        return buttons_message(owner, reply, [("book", "Book another"), ("my bookings", "My bookings"), ("human", "Talk to a person")]), calls, "confirmation"
    if normalized.startswith("slot:"):
        selected = body.strip()[5:]
        if selected not in state.get("offered_slots", []):
            call("refuse_out_of_scope")
            return text_message(owner, "Please choose one of the offered times."), calls, "invalid_choice"
        state["pending_slot"] = selected
        convo.state = state
        return buttons_message(owner, "Confirm this appointment time?", [("confirm", "Confirm"), ("no", "Start over"), ("human", "Talk to a person")]), calls, "confirm_prompt"
    if normalized.startswith("booking:"):
        selected = body.strip()[8:]
        if selected not in state.get("offered_bookings", []):
            call("refuse_out_of_scope", ToolArgs(category="other_patient_data"))
            return text_message(owner, REFUSALS["other_patient_data"]), calls, "other_patient_data"
        if state.get("intent") == "cancel":
            result = call("cancel_booking", ToolArgs(booking_id=selected))
            convo.state = {}
            return text_message(owner, "Your appointment is cancelled." if result.result.ok else "Unable to cancel this appointment."), calls, "cancel"
        state["booking_id"] = selected
        state["intent"] = "reschedule"
    elif re.search(r"cancel|reschedule|move|my bookings|my appointments", normalized):
        result = call("get_my_bookings", ToolArgs(patient_wa_id=owner))
        if not result.result.ids:
            return text_message(owner, "You have no active appointments."), calls, "bookings_empty"
        state = {"intent": "cancel" if "cancel" in normalized else "reschedule" if re.search(r"reschedule|move", normalized) else "view", "offered_bookings": result.result.ids}
        convo.state = state
        if state["intent"] == "view":
            return text_message(owner, "Your active appointment references: " + ", ".join(result.result.ids)), calls, "bookings"
        return list_message(owner, "Choose your appointment.", [{"id": "booking:" + key, "title": "Appointment " + str(i + 1), "description": key} for i, key in enumerate(result.result.ids[:10])]), calls, "booking_choice"
    chosen = next((service for service in services if normalized == "service:" + service.id or service.name.lower() in normalized), None)
    if chosen:
        state["service_id"] = chosen.id
    date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", normalized)
    if date_match:
        try:
            requested = datetime.fromisoformat(date_match[0]).replace(tzinfo=ZoneInfo(clinic.timezone))
            delta = (requested.date() - now().astimezone(ZoneInfo(clinic.timezone)).date()).days
            if not 0 <= delta < clinic.booking_horizon_days:
                raise ValueError("Outside horizon")
            state["date_from"] = requested.astimezone(UTC).isoformat()
            state["date_to"] = (requested + timedelta(days=1)).astimezone(UTC).isoformat()
        except ValueError:
            call("check_availability", ToolArgs(date_from="1900-01-01", date_to="1900-01-02"))
            convo.state = {}
            return text_message(owner, "Please choose a valid date within the booking horizon."), calls, "invalid_date"
    if state.get("service_id"):
        result = call("check_availability", ToolArgs(service_id=state["service_id"], date_from=state.get("date_from"), date_to=state.get("date_to")))
        state["offered_slots"] = result.result.ids
        state.pop("pending_slot", None)
        convo.state = state
        rows = []
        for key in result.result.ids:
            slot = session.exec(select(Slot).where(Slot.id == key, Slot.clinic_id == clinic.id)).one()
            local = slot.starts_at.astimezone(ZoneInfo(clinic.timezone))
            rows.append({"id": "slot:" + key, "title": local.strftime("%a %b %d %I:%M %p")[:24], "description": local.tzname() or clinic.timezone})
        if rows:
            return list_message(owner, "Choose an available time. Times use the clinic timezone.", rows), calls, "availability"
        return text_message(owner, "No times are available for that request. Try another date or talk to a person."), calls, "no_availability"
    if re.search(r"book|appointment|visit|hello|hi\b|schedule|available|morning|afternoon|tomorrow", normalized) or normalized in {"", "no", "start over", "back"} or state.get("booking_id"):
        convo.state = state
        return list_message(owner, "Welcome to fictional Ridgeview. Booking logistics only. Please choose a service.", [{"id": "service:" + service.id, "title": service.name} for service in services]), calls, "service_prompt"
    call("refuse_out_of_scope")
    return text_message(owner, REFUSALS["unrelated"]), calls, "unrelated"

def ingest(db: Engine, phone_id: str, owner: str, wamid: str, body: str, timestamp: datetime) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,160}", wamid) or not re.fullmatch(r"[0-9]{5,20}", owner):
        raise ValueError("Invalid identifier")
    if timestamp > now() + timedelta(minutes=5):
        raise ValueError("Invalid timestamp")
    with Session(db) as session:
        clinic = session.exec(select(Clinic).where(Clinic.whatsapp_phone_number_id == phone_id)).first()
        if clinic is None:
            raise Denied("Unknown phone identity")
        lock_conversation(session, clinic.id, owner)
        duplicate = session.exec(select(Message).where(Message.wamid == wamid, Message.clinic_id == clinic.id)).first()
        if duplicate:
            return {"duplicate": True, "conversation_id": duplicate.conversation_id, "clinic_id": clinic.id}
        convo = session.exec(select(Conversation).where(Conversation.clinic_id == clinic.id, Conversation.wa_id == owner)).first()
        if convo is None:
            convo = Conversation(clinic_id=clinic.id, wa_id=owner, last_inbound_at=timestamp)
            session.add(convo)
            session.flush()
        convo.last_inbound_at = max(convo.last_inbound_at, timestamp)
        convo.last_message_id = wamid
        payload, calls, summary = respond(session, clinic, convo, body)
        if not can_send_free_form(convo.last_inbound_at):
            payload = template_message(owner)
        convo.state = {**convo.state, "recent": (convo.state.get("recent", []) + [summary])[-6:]}
        message = Message(clinic_id=clinic.id, conversation_id=convo.id, direction="inbound", wamid=wamid, content_summary=summary, tool_calls=[call.model_dump() for call in calls])
        session.add(message)
        session.add(convo)
        session.add(Outbox(clinic_id=clinic.id, conversation_id=convo.id, message_id=wamid, payload=payload))
        session.flush()
        session.add(Message(clinic_id=clinic.id, conversation_id=convo.id, direction="outbound", wamid="out:" + wamid, content_summary=str(payload.get("text", {}).get("body") or payload.get("interactive", {}).get("body", {}).get("text") or "Approved template"), tool_calls=[]))
        result = {"duplicate": False, "conversation_id": convo.id, "clinic_id": clinic.id, "reply": payload, "calls": [call.model_dump() for call in calls]}
        session.commit()
        return result


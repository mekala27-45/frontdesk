from datetime import UTC, datetime

from frontdesk_core.contracts import ToolArgs, ToolCall, ToolName, ToolResult
from frontdesk_core.models import Booking, Conversation, Escalation, Provider, Service, Slot
from frontdesk_scheduling.engine import Denied, Unavailable, cancel, claim, own_booking
from sqlmodel import Session, col, select


def invoke(
    session: Session, clinic: str, owner: str, conversation_id: str, name: ToolName, args: ToolArgs
) -> ToolCall:
    conversation = session.exec(
        select(Conversation).where(
            Conversation.clinic_id == clinic,
            Conversation.id == conversation_id,
            Conversation.wa_id == owner,
        )
    ).first()
    if conversation is None:
        raise Denied("Conversation outside caller scope")
    if args.patient_wa_id is not None and args.patient_wa_id != owner:
        raise Denied("Owner mismatch")
    if (
        args.service_id
        and session.exec(
            select(Service).where(Service.id == args.service_id, Service.clinic_id == clinic)
        ).first()
        is None
    ):
        raise Denied("Resource outside caller scope")
    if (
        args.provider_id
        and session.exec(
            select(Provider).where(Provider.id == args.provider_id, Provider.clinic_id == clinic)
        ).first()
        is None
    ):
        raise Denied("Resource outside caller scope")
    try:
        ids: list[str] = []
        if name == "check_availability":
            query = select(Slot).where(Slot.clinic_id == clinic, Slot.status == "open")
            if args.service_id:
                query = query.where(Slot.service_id == args.service_id)
            if args.provider_id:
                query = query.where(Slot.provider_id == args.provider_id)
            if args.date_from:
                query = query.where(
                    Slot.starts_at >= datetime.fromisoformat(args.date_from).replace(tzinfo=UTC)
                )
            if args.date_to:
                query = query.where(
                    Slot.starts_at < datetime.fromisoformat(args.date_to).replace(tzinfo=UTC)
                )
            from datetime import timedelta

            from frontdesk_core.contracts import now
            from frontdesk_core.models import Clinic

            rules = session.exec(select(Clinic).where(Clinic.id == clinic)).one()
            query = query.where(
                Slot.starts_at >= now() + timedelta(minutes=rules.min_notice_minutes),
                Slot.starts_at < now() + timedelta(days=rules.booking_horizon_days),
            )
            candidates = session.exec(query.order_by(col(Slot.starts_at)).limit(100)).all()
            for slot in candidates:
                conflict = session.exec(
                    select(Slot).where(
                        Slot.clinic_id == clinic,
                        Slot.provider_id == slot.provider_id,
                        col(Slot.status).in_(["booked", "blocked"]),
                        Slot.starts_at < slot.ends_at,
                        Slot.ends_at > slot.starts_at,
                    )
                ).first()
                if not conflict:
                    ids.append(slot.id)
                if len(ids) == 8:
                    break
        elif name == "book_slot":
            ids = [claim(session, clinic, owner, args.slot_id or "").id]
        elif name == "reschedule_booking":
            booking = own_booking(session, clinic, owner, args.booking_id or "")
            ids = [claim(session, clinic, owner, args.slot_id or "", booking).id]
        elif name == "cancel_booking":
            ids = [cancel(session, clinic, owner, args.booking_id or "").id]
        elif name == "get_my_bookings":
            ids = [
                booking.id
                for booking in session.exec(
                    select(Booking).where(
                        Booking.clinic_id == clinic,
                        Booking.patient_wa_id == owner,
                        Booking.status == "confirmed",
                    )
                ).all()
            ]
        elif name == "escalate_to_human":
            existing = session.exec(
                select(Escalation).where(
                    Escalation.clinic_id == clinic,
                    Escalation.conversation_id == conversation_id,
                    col(Escalation.resolved_at).is_(None),
                )
            ).first()
            if existing is None:
                existing = Escalation(
                    clinic_id=clinic, conversation_id=conversation_id, reason=args.category
                )
                session.add(existing)
                session.flush()
            conversation.status = "escalated"
            session.add(conversation)
            ids = [existing.id]
        elif name == "refuse_out_of_scope":
            pass
        result = ToolResult(ok=True, code="ok", ids=ids)
    except Unavailable:
        result = ToolResult(ok=False, code="no_longer_available")
    return ToolCall(name=name, arguments=args, result=result)

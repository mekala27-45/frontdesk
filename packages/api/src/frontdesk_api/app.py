import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from frontdesk_agent.engine import ingest
from frontdesk_agent.llm import LiteLLMPolicy
from frontdesk_calendar.adapters import (
    CalendarAdapter,
    GoogleCalendarAdapter,
    NullCalendarAdapter,
    sync_pending,
)
from frontdesk_core.config import Settings
from frontdesk_core.contracts import StrictModel, now
from frontdesk_core.db import engine
from frontdesk_core.models import (
    Booking,
    Clinic,
    Conversation,
    Escalation,
    Evidence,
    Message,
    Outbox,
    Provider,
    Service,
    Slot,
)
from frontdesk_scheduling.engine import Denied, Unavailable, claim
from frontdesk_whatsapp.protocol import verify
from frontdesk_whatsapp.transport import DevTransport, MetaTransport, WhatsAppTransport, dispatch
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select
from starlette.concurrency import run_in_threadpool

from frontdesk_api.reminders import run


class ClaimRequest(StrictModel):
    clinic_id: str
    wa_id: str
    slot_id: str


def create_app(
    settings: Settings | None = None,
    db: Engine | None = None,
    transport: WhatsAppTransport | None = None,
    calendar: CalendarAdapter | None = None,
    policy: LiteLLMPolicy | None = None,
) -> FastAPI:
    settings = settings or Settings()
    db = db or engine(settings.database_url)
    if (
        policy is None
        and settings.llm_model
        and any(os.getenv(key) for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"))
    ):
        policy = LiteLLMPolicy(settings.llm_model, settings.llm_budget_usd, db)
    transport = transport or (MetaTransport(settings) if settings.meta_token else DevTransport())
    calendar = calendar or (
        GoogleCalendarAdapter(settings) if settings.google_calendar_id else NullCalendarAdapter()
    )
    app = FastAPI(title="Frontdesk, fictional logistics only")
    app.state.db, app.state.transport, app.state.settings = db, transport, settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.exception_handler(RequestValidationError)
    async def invalid(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse({"detail": "Malformed logistics request"}, status_code=422)

    def ops(request: Request) -> None:
        if not hmac.compare_digest(
            request.headers.get("authorization", ""), "Bearer " + settings.ops_token
        ):
            raise HTTPException(401, "Ops token required")

    async def body_bytes(request: Request) -> bytes:
        result = b""
        async for chunk in request.stream():
            result += chunk
            if len(result) > 16384:
                raise HTTPException(413, "Payload too large")
        return result

    def process(payload: dict[str, Any], demo_owner: str | None = None) -> dict[str, Any]:
        results = []
        try:
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    value = change["value"]
                    phone = value["metadata"]["phone_number_id"]
                    messages = value.get("messages", [])
                    if len(messages) > 10:
                        raise ValueError("Batch limit")
                    for message in messages:
                        owner = message["from"]
                        if demo_owner is not None and (
                            owner != demo_owner or phone != "demo-phone"
                        ):
                            raise Denied("Simulator identity mismatch")
                        kind = message["type"]
                        if kind == "text":
                            body = message["text"]["body"]
                        elif kind == "interactive":
                            interactive = message["interactive"]
                            body = interactive[interactive["type"]]["id"]
                        else:
                            body = "unsupported"
                        if not isinstance(body, str) or len(body) > 4096:
                            raise ValueError("Invalid message")
                        timestamp = datetime.fromtimestamp(int(message["timestamp"]), UTC)
                        result = ingest(db, phone, owner, message["id"], body, timestamp, policy)
                        dispatch(
                            db,
                            DevTransport() if demo_owner is not None else transport,
                            result["clinic_id"],
                            phone,
                        )
                        results.append(result)
            sync_pending(db, calendar)
        except Denied as exc:
            raise HTTPException(403, "Resource outside caller scope") from exc
        except (
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            IndexError,
            OverflowError,
            IntegrityError,
        ) as exc:
            raise HTTPException(400, "Malformed or conflicting webhook") from exc
        return {"results": results}

    @app.post("/ops/claim")
    def claim_slot(request: Request, body: ClaimRequest) -> dict[str, str]:
        ops(request)
        try:
            with Session(db) as session:
                booking = claim(session, body.clinic_id, body.wa_id, body.slot_id)
                identity = booking.id
                session.commit()
            return {"status": "confirmed", "booking_id": identity}
        except Unavailable as exc:
            raise HTTPException(409, "No longer available") from exc
        except Denied as exc:
            raise HTTPException(403, "Resource outside caller scope") from exc

    @app.get("/health")
    def health() -> dict[str, str]:
        with Session(db) as session:
            session.exec(select(Clinic).limit(1)).first()
        return {"status": "ok", "transport": "meta" if settings.meta_token else "dev"}

    @app.get("/webhooks/whatsapp", response_class=PlainTextResponse)
    def verify_webhook(request: Request) -> str:
        params = request.query_params
        if params.get("hub.mode") != "subscribe" or not hmac.compare_digest(
            params.get("hub.verify_token", ""), settings.verify_token
        ):
            raise HTTPException(403, "Verification denied")
        return params.get("hub.challenge", "")

    @app.post("/webhooks/whatsapp")
    async def webhook(request: Request) -> dict[str, Any]:
        raw = await body_bytes(request)
        if not verify(raw, request.headers.get("x-hub-signature-256", ""), settings.app_secret):
            raise HTTPException(403, "Signature denied")
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError()
        except (ValueError, UnicodeDecodeError) as exc:
            raise HTTPException(400, "Malformed webhook") from exc
        return await run_in_threadpool(process, payload)

    @app.post("/internal/simulator/session")
    def demo_session() -> dict[str, str]:
        owner = "999" + str(secrets.randbelow(10**10)).zfill(10)
        expires = str(int(now().timestamp()) + 3600)
        signature = hmac.new(
            settings.simulator_secret.encode(), (owner + "." + expires).encode(), hashlib.sha256
        ).hexdigest()
        return {"wa_id": owner, "token": owner + "." + expires + "." + signature}

    @app.post("/internal/simulator")
    async def simulator(request: Request) -> dict[str, Any]:
        token = request.headers.get("authorization", "").removeprefix("Bearer ")
        try:
            owner, expires, signature = token.split(".")
            expected = hmac.new(
                settings.simulator_secret.encode(), (owner + "." + expires).encode(), hashlib.sha256
            ).hexdigest()
            if int(expires) < now().timestamp() or not hmac.compare_digest(signature, expected):
                raise ValueError()
            raw = await body_bytes(request)
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError()
        except (ValueError, UnicodeDecodeError) as exc:
            raise HTTPException(401, "Simulator session required") from exc
        return await run_in_threadpool(process, payload, owner)

    @app.post("/internal/reminders")
    def reminders(request: Request) -> dict[str, int]:
        try:
            result = run(
                db,
                request.headers.get("x-timestamp", ""),
                request.headers.get("x-nonce", ""),
                request.headers.get("x-signature", ""),
                settings.reminder_secret,
            )
        except (PermissionError, ValueError) as exc:
            raise HTTPException(403, "Reminder authentication denied") from exc
        with Session(db) as session:
            clinics = session.exec(select(Clinic)).all()
            for clinic in clinics:
                dispatch(db, transport, clinic.id, clinic.whatsapp_phone_number_id)
        sync_pending(db, calendar)
        return result

    @app.get("/ops")
    def console(request: Request, clinic_id: str = "") -> dict[str, Any]:
        ops(request)
        with Session(db) as session:
            clinic = (
                session.exec(select(Clinic).where(Clinic.id == clinic_id)).first()
                if clinic_id
                else session.exec(
                    select(Clinic).where(Clinic.whatsapp_phone_number_id == "demo-phone")
                ).first()
            )
            if clinic is None:
                raise HTTPException(404, "Clinic unavailable")
            day = (
                now()
                .astimezone(ZoneInfo(clinic.timezone))
                .replace(hour=0, minute=0, second=0, microsecond=0)
            )
            bookings = session.exec(
                select(Booking, Slot)
                .join(Slot, col(Slot.id) == col(Booking.slot_id))
                .where(
                    Booking.clinic_id == clinic.id,
                    Slot.clinic_id == clinic.id,
                    Slot.starts_at >= day,
                    Slot.starts_at < day + timedelta(days=1),
                )
            ).all()
            return {
                "clinic": clinic.model_dump(),
                "bookings": [
                    {
                        "id": b.id,
                        "status": b.status,
                        "provider_id": s.provider_id,
                        "starts_at": s.starts_at.isoformat(),
                    }
                    for b, s in bookings
                ],
                "providers": [
                    p.model_dump()
                    for p in session.exec(
                        select(Provider).where(Provider.clinic_id == clinic.id)
                    ).all()
                ],
                "services": [
                    s.model_dump()
                    for s in session.exec(
                        select(Service).where(Service.clinic_id == clinic.id)
                    ).all()
                ],
                "escalations": [
                    e.model_dump()
                    for e in session.exec(
                        select(Escalation).where(
                            Escalation.clinic_id == clinic.id, col(Escalation.resolved_at).is_(None)
                        )
                    ).all()
                ],
                "conversations": [
                    {
                        "id": c.id,
                        "status": c.status,
                        "last_inbound_at": c.last_inbound_at.isoformat(),
                    }
                    for c in session.exec(
                        select(Conversation)
                        .where(Conversation.clinic_id == clinic.id)
                        .order_by(col(Conversation.last_inbound_at).desc())
                        .limit(100)
                    ).all()
                ],
                "utilization": [
                    {
                        "provider_id": p.id,
                        "open": len(
                            session.exec(
                                select(Slot).where(
                                    Slot.clinic_id == clinic.id,
                                    Slot.provider_id == p.id,
                                    Slot.status == "open",
                                )
                            ).all()
                        ),
                        "booked": len(
                            session.exec(
                                select(Slot).where(
                                    Slot.clinic_id == clinic.id,
                                    Slot.provider_id == p.id,
                                    Slot.status == "booked",
                                )
                            ).all()
                        ),
                    }
                    for p in session.exec(
                        select(Provider).where(Provider.clinic_id == clinic.id)
                    ).all()
                ],
                "evidence": {e.name: e.value for e in session.exec(select(Evidence)).all()},
            }

    @app.get("/ops/replay/{conversation_id}")
    def replay(request: Request, conversation_id: str, clinic_id: str) -> dict[str, Any]:
        ops(request)
        with Session(db) as session:
            if (
                session.exec(
                    select(Conversation).where(
                        Conversation.id == conversation_id, Conversation.clinic_id == clinic_id
                    )
                ).first()
                is None
            ):
                raise HTTPException(403, "Conversation unavailable")
            messages = session.exec(
                select(Message)
                .where(Message.clinic_id == clinic_id, Message.conversation_id == conversation_id)
                .order_by(col(Message.created_at), col(Message.id))
            ).all()
            outbox = session.exec(
                select(Outbox).where(
                    Outbox.clinic_id == clinic_id, Outbox.conversation_id == conversation_id
                )
            ).all()
            return {
                "messages": [m.model_dump() for m in messages],
                "delivery": [{"status": o.status, "message_id": o.message_id} for o in outbox],
            }

    @app.post("/ops/escalations/{identity}/resolve")
    def resolve(request: Request, identity: str, clinic_id: str) -> dict[str, bool]:
        ops(request)
        with Session(db) as session:
            row = session.exec(
                select(Escalation).where(
                    Escalation.id == identity, Escalation.clinic_id == clinic_id
                )
            ).first()
            if row is None:
                raise HTTPException(403, "Escalation unavailable")
            row.resolved_at, row.resolved_by = now(), "demo-operator"
            convo = session.exec(
                select(Conversation).where(
                    Conversation.id == row.conversation_id, Conversation.clinic_id == clinic_id
                )
            ).one()
            convo.status, convo.state = "active", {}
            session.add(row)
            session.add(convo)
            session.commit()
        return {"ok": True}

    return app


app = create_app()

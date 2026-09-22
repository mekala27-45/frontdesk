import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import pytest
from conftest import evidence, make_clinic
from frontdesk_agent.engine import ingest
from frontdesk_core.contracts import now, uuid7
from frontdesk_core.models import Booking, Conversation, Message
from frontdesk_scheduling.slots import intervals
from sqlmodel import Session, col, select

from redteam.score import score


def test_safety_scoring_clean_violation_empty():
    turn = {
        "content_summary": "unrelated",
        "tool_calls": [
            {
                "name": "refuse_out_of_scope",
                "arguments": {"category": "unrelated"},
                "result": {"ok": True},
            }
        ],
    }
    assert score("injection", [], [turn], [True])["passed"]
    assert not score(
        "injection", [], [{"content_summary": "safe sounding prose", "tool_calls": []}], [True]
    )["passed"]
    with pytest.raises(ValueError):
        score("injection", [], [], [])
    assert not score("booking", [], [turn], [False])["passed"]


def test_fifty_scenarios(db):
    paths = sorted(Path("redteam/scenarios").glob("*.json"))
    assert len(paths) == 50
    results = []
    for path in paths:
        spec = json.loads(path.read_text())
        with Session(db) as session:
            clinic, _, services, slots, convo = make_clinic(session)
        replacements = {"$service_id": services[spec.get("service_index", 0)].id}
        owner = convo.wa_id
        current = None
        confirmations = []
        selected = None
        for phrase in spec["turns"]:
            if phrase == "$service":
                phrase = "service:" + replacements["$service_id"]
            if phrase == "$slot":
                phrase = current["reply"]["interactive"]["action"]["sections"][0]["rows"][0]["id"]
                replacements["$selected_slot"] = phrase.removeprefix("slot:")
                selected = replacements["$selected_slot"]
            if phrase == "$booking":
                phrase = current["reply"]["interactive"]["action"]["sections"][0]["rows"][0]["id"]
                replacements["$booking_id"] = phrase.removeprefix("booking:")
            if spec["kind"] == "race" and phrase == "confirm":
                rival = "15550002222"
                with Session(db) as session:
                    session.add(
                        Conversation(
                            clinic_id=clinic.id, wa_id=rival, state={"pending_slot": selected}
                        )
                    )
                    session.commit()
                with ThreadPoolExecutor(max_workers=2) as pool:
                    responses = list(
                        pool.map(
                            lambda who, phone=clinic.whatsapp_phone_number_id: ingest(
                                db, phone, who, uuid7(), "confirm", now()
                            ),
                            [owner, rival],
                        )
                    )
                with Session(db) as session:
                    bookings = session.exec(
                        select(Booking).where(
                            Booking.clinic_id == clinic.id, Booking.slot_id == selected
                        )
                    ).all()
                    assert len(bookings) == 1
                assert sum(r["calls"][0]["result"]["ok"] for r in responses) == 1
                # Score the winning caller's persisted audit record.
                current = next(r for r in responses if r["calls"][0]["result"]["ok"])
                owner = next(
                    who for who, r in zip([owner, rival], responses, strict=True) if r is current
                )
            else:
                current = ingest(db, clinic.whatsapp_phone_number_id, owner, uuid7(), phrase, now())
            with Session(db) as session:
                reply_text = str(
                    current["reply"].get("text", {}).get("body")
                    or current["reply"].get("interactive", {}).get("body", {}).get("text")
                    or ""
                )
                if "appointment is confirmed" in reply_text:
                    confirmations.append(
                        any(
                            call["name"] in {"book_slot", "reschedule_booking"}
                            and call["result"]["ok"]
                            and call["result"]["ids"]
                            for call in current["calls"]
                        )
                    )
                for call in current["calls"]:
                    if call["name"] in {"book_slot", "reschedule_booking"} and call["result"]["ok"]:
                        confirmations.append(
                            all(
                                session.exec(
                                    select(Booking).where(
                                        Booking.id == identity,
                                        Booking.clinic_id == clinic.id,
                                        Booking.patient_wa_id == owner,
                                        Booking.status == "confirmed",
                                    )
                                ).first()
                                is not None
                                for identity in call["result"]["ids"]
                            )
                        )
                if not current["calls"] or not any(
                    call["name"] in {"book_slot", "reschedule_booking"} for call in current["calls"]
                ):
                    confirmations.append(True)
        boundary = True
        if spec["kind"] == "dst":
            boundary = len(intervals(date(2026, 3, 8), "America/New_York", 0, 5, 30)) == 8
        elif spec["kind"] == "closing":
            values = intervals(date(2026, 9, 22), "America/New_York", 9, 17, 30)
            from zoneinfo import ZoneInfo

            boundary = (
                all(end.astimezone(ZoneInfo("America/New_York")).hour <= 17 for _, end in values)
                and values[-1][1].astimezone(ZoneInfo("America/New_York")).hour == 17
            )
        elif spec["kind"] == "session":
            with Session(db) as session:
                row = session.get(Conversation, convo.id)
                row.last_inbound_at = now() - timedelta(hours=24, seconds=1)
                session.add(row)
                session.commit()
            current = ingest(
                db,
                clinic.whatsapp_phone_number_id,
                owner,
                uuid7(),
                "book",
                now() - timedelta(hours=24, seconds=1),
            )
            boundary = current["reply"]["type"] == "template"
        expected = [
            {
                "name": e["name"],
                "arguments": {k: replacements.get(v, v) for k, v in e["arguments"].items()},
            }
            for e in spec["expected"]
        ]
        with Session(db) as session:
            conversation = session.exec(
                select(Conversation).where(
                    Conversation.clinic_id == clinic.id, Conversation.wa_id == owner
                )
            ).one()
            turns = session.exec(
                select(Message)
                .where(
                    Message.clinic_id == clinic.id,
                    Message.conversation_id == conversation.id,
                    Message.direction == "inbound",
                )
                .order_by(col(Message.created_at), col(Message.id))
            ).all()
            replay = [
                {"content_summary": t.content_summary, "tool_calls": t.tool_calls} for t in turns
            ]
            result = score(
                spec["category"],
                expected,
                replay,
                confirmations or [True],
                spec.get("expected_summary"),
            )
        if not boundary:
            result["passed"] = False
            result["failures"].append("window_violation")
        results.append(
            {
                "id": spec["id"],
                "category": spec["category"],
                "conversation_id": current["conversation_id"],
                "clinic_id": clinic.id,
                "expected": expected,
                "expected_summary": spec.get("expected_summary"),
                **result,
                "replay": replay,
            }
        )
    categories = {}
    for result in results:
        group = categories.setdefault(result["category"], {"passed": 0, "total": 0})
        group["total"] += 1
        group["passed"] += int(result["passed"])
    evidence(
        db,
        "redteam",
        {
            "total": len(results),
            "passed": sum(r["passed"] for r in results),
            "categories": categories,
            "scenarios": results,
        },
    )
    assert all(r["passed"] for r in results), [
        (r["id"], r["failures"]) for r in results if not r["passed"]
    ]

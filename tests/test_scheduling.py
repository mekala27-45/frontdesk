import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import httpx
import pytest
from conftest import evidence
from frontdesk_api.app import create_app
from frontdesk_core.models import Booking, Slot
from frontdesk_scheduling.engine import Unavailable, cancel, claim, own_booking
from frontdesk_scheduling.slots import generate, intervals
from hypothesis import given
from hypothesis import strategies as st
from sqlmodel import Session, select


@pytest.mark.external
async def test_fifty_concurrent_claims(db, clinic):
    c, _, _, slots, _ = clinic
    app = create_app(db=db)
    # Warm the connection pool; measured interval covers the simultaneous HTTP calls.
    with ThreadPoolExecutor(max_workers=50) as pool:
        connections = list(pool.map(lambda _: db.connect(), range(50)))
    for connection in connections:
        connection.close()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        started = time.perf_counter()
        results = await asyncio.gather(
            *[
                client.post(
                    "/ops/claim",
                    headers={"Authorization": "Bearer local-ops-token"},
                    json={"clinic_id": c.id, "wa_id": str(15550000000 + i), "slot_id": slots[0].id},
                )
                for i in range(50)
            ]
        )
        elapsed = time.perf_counter() - started
    codes = [r.status_code for r in results]
    with Session(db) as session:
        count = len(
            session.exec(
                select(Booking).where(Booking.clinic_id == c.id, Booking.slot_id == slots[0].id)
            ).all()
        )
    measured = {
        "requests": 50,
        "confirmed": codes.count(200),
        "rejected": codes.count(409),
        "errors": sum(x not in (200, 409) for x in codes),
        "booking_rows": count,
        "duration_seconds": round(elapsed, 6),
        "under_two_seconds": elapsed < 2,
        "pool": "warm",
        "transport": "HTTP ASGI client to real Postgres",
    }
    evidence(db, "concurrency", measured)
    assert codes.count(200) == count == 1
    assert codes.count(409) == 49
    assert elapsed < 2


def test_dst(db):
    ordinary = intervals(date(2026, 3, 7), "America/New_York", 0, 5, 30)
    spring = intervals(date(2026, 3, 8), "America/New_York", 0, 5, 30)
    fall = intervals(date(2026, 11, 1), "America/New_York", 0, 5, 30)
    from zoneinfo import ZoneInfo

    assert len(ordinary) == 10 and len(spring) == 8 and len(fall) == 12
    assert all(start.astimezone(ZoneInfo("America/New_York")).hour != 2 for start, _ in spring)
    assert len({s for s, _ in fall}) == len(fall)
    evidence(
        db,
        "dst",
        {
            "timezone": "America/New_York",
            "ordinary_slots": len(ordinary),
            "spring_slots": len(spring),
            "fall_slots": len(fall),
            "spring_date": "2026-03-08",
            "fall_date": "2026-11-01",
        },
    )


@given(st.integers(min_value=1, max_value=120))
def test_slot_intervals_are_disjoint(minutes):
    values = intervals(date(2026, 3, 8), "America/New_York", 0, 5, minutes)
    assert all(a < b for a, b in values)
    assert all(values[i][1] <= values[i + 1][0] for i in range(len(values) - 1))


def test_atomic_move_and_cancel(db, clinic):
    c, _, _, slots, _ = clinic
    with Session(db) as session:
        first = claim(session, c.id, "15550001111", slots[0].id)
        claim(session, c.id, "15550002222", slots[1].id)
        identity = first.id
        session.commit()
    with Session(db) as session:
        with pytest.raises(Unavailable):
            claim(
                session,
                c.id,
                "15550001111",
                slots[1].id,
                own_booking(session, c.id, "15550001111", identity),
            )
        session.rollback()
    with Session(db) as session:
        assert session.get(Booking, identity).slot_id == slots[0].id
        moved = claim(
            session,
            c.id,
            "15550001111",
            slots[2].id,
            own_booking(session, c.id, "15550001111", identity),
        )
        assert moved.slot_id == slots[2].id
        session.commit()
    with Session(db) as session:
        cancel(session, c.id, "15550001111", identity)
        cancel(session, c.id, "15550001111", identity)
        session.commit()
        assert session.get(Slot, slots[2].id).status == "open"


def test_overlapping_services_and_notice(db, clinic):
    c, p, services, slots, _ = clinic
    with Session(db) as session:
        overlap = Slot(
            clinic_id=c.id,
            provider_id=p.id,
            service_id=services[1].id,
            starts_at=slots[0].starts_at,
            ends_at=slots[0].ends_at,
        )
        session.add(overlap)
        session.commit()
        claim(session, c.id, "15550001111", slots[0].id)
        session.commit()
        with pytest.raises(Unavailable):
            claim(session, c.id, "15550002222", overlap.id)
        session.rollback()
        slot = session.get(Slot, slots[1].id)
        from frontdesk_core.contracts import now

        slot.starts_at = now() - timedelta(hours=1)
        session.add(slot)
        session.commit()
        with pytest.raises(Unavailable):
            claim(session, c.id, "15550001111", slot.id)


def test_generation_idempotent(db, clinic):
    c, _, _, _, _ = clinic
    with Session(db) as session:
        assert generate(session, c.id) > 0
        assert generate(session, c.id) == 0


def test_invalid_interval():
    with pytest.raises(ValueError):
        intervals(date(2026, 3, 8), "UTC", 9, 8, 30)

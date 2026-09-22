import pytest
from conftest import evidence, make_clinic
from frontdesk_agent.tools import invoke
from frontdesk_core.contracts import ToolArgs
from frontdesk_scheduling.engine import Denied, claim
from sqlmodel import Session


def tenant_gate(checks):
    if not checks:
        raise ValueError("No tenant checks")
    return all(checks)


def test_tenant_gate_three_cases():
    assert tenant_gate([True])
    assert not tenant_gate([True, False])
    with pytest.raises(ValueError):
        tenant_gate([])


def test_tenant_isolation(db, clinic):
    a, _, _, slots_a, conv_a = clinic
    with Session(db) as session:
        b, p_b, services_b, slots_b, conv_b = make_clinic(session)
        booking = claim(session, b.id, conv_b.wa_id, slots_b[0].id)
        booking_id = booking.id
        session.commit()
    checks = []
    cases = [
        ("check_availability", ToolArgs(service_id=services_b[0].id)),
        ("check_availability", ToolArgs(provider_id=p_b.id)),
        ("book_slot", ToolArgs(slot_id=slots_b[1].id)),
        ("reschedule_booking", ToolArgs(booking_id=booking_id, slot_id=slots_a[0].id)),
        ("cancel_booking", ToolArgs(booking_id=booking_id)),
        ("get_my_bookings", ToolArgs(patient_wa_id="15550009999")),
        ("escalate_to_human", ToolArgs()),
        ("refuse_out_of_scope", ToolArgs()),
    ]
    for name, args in cases:
        with Session(db) as session:
            with pytest.raises(Denied):
                invoke(
                    session,
                    a.id,
                    conv_a.wa_id,
                    conv_b.id
                    if name in {"escalate_to_human", "refuse_out_of_scope"}
                    else conv_a.id,
                    name,
                    args,
                )
            checks.append(True)
    for name in [
        "check_availability",
        "book_slot",
        "reschedule_booking",
        "cancel_booking",
        "get_my_bookings",
        "escalate_to_human",
        "refuse_out_of_scope",
    ]:
        with Session(db) as session:
            with pytest.raises(Denied):
                invoke(session, b.id, conv_b.wa_id, conv_a.id, name, ToolArgs())
            checks.append(True)
    assert tenant_gate(checks)
    evidence(
        db, "tenant", {"attempts": len(checks), "explicitly_refused": sum(checks), "passed": True}
    )

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import pytest
from frontdesk_agent.llm import BudgetExceeded, LiteLLMPolicy
from frontdesk_calendar.adapters import GoogleCalendarAdapter, NullCalendarAdapter
from frontdesk_core.config import Settings
from frontdesk_whatsapp.transport import MetaTransport
from googleapiclient.errors import HttpError

from redteam.judge import LiteLLMJudge


def test_meta_transport_contract():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"messages": [{"id": "wamid.test"}]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    transport = MetaTransport(Settings(meta_token="test-token"), client)
    body = {
        "messaging_product": "whatsapp",
        "to": "15550001111",
        "type": "text",
        "text": {"body": "Logistics only."},
    }
    assert transport.send(body, "phone") == "wamid.test"
    assert str(seen[0].url) == "https://graph.facebook.com/v23.0/phone/messages"
    assert seen[0].headers["authorization"] == "Bearer test-token"
    assert json.loads(seen[0].content) == body


def test_google_insert_update_delete(clinic):
    from frontdesk_core.models import Booking

    c, _, _, slots, _ = clinic
    booking = Booking(
        clinic_id=c.id,
        slot_id=slots[0].id,
        patient_wa_id="15550001111",
        service_id=slots[0].service_id,
    )
    service = MagicMock()
    adapter = GoogleCalendarAdapter(Settings(google_calendar_id="fictional"), service)
    expected = booking.id.replace("-", "")
    assert adapter.sync(booking, slots[0]) == expected
    body = service.events().insert.call_args.kwargs["body"]
    assert "15550001111" not in str(body)
    service.events().insert().execute.side_effect = HttpError(
        SimpleNamespace(status=409, reason="Conflict"), b"{}"
    )
    assert adapter.sync(booking, slots[0]) == expected
    assert service.events().update.called
    booking.status = "cancelled"
    adapter.sync(booking, slots[0])
    assert service.events().delete.called
    service.events().delete().execute.side_effect = HttpError(
        SimpleNamespace(status=404, reason="Missing"), b"{}"
    )
    assert adapter.sync(booking, slots[0]) == expected
    service.events().delete().execute.side_effect = HttpError(
        SimpleNamespace(status=500, reason="Failure"), b"{}"
    )
    with pytest.raises(HttpError):
        adapter.sync(booking, slots[0])
    assert NullCalendarAdapter().sync(booking, slots[0]).startswith("null:")


def test_optional_model_forced_output_and_budget(monkeypatch):
    import litellm

    calls = []
    monkeypatch.setattr(litellm, "cost_per_token", lambda **kwargs: (0.001, 0.001))

    def complete(**kwargs):
        calls.append(kwargs)
        arguments = (
            '{"intent":"book"}'
            if kwargs["tool_choice"]["function"]["name"] == "choose_intent"
            else '{"clarity":5,"tone":4}'
        )
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        tool_calls=[SimpleNamespace(function=SimpleNamespace(arguments=arguments))]
                    )
                )
            ]
        )

    monkeypatch.setattr(litellm, "completion", complete)
    policy = LiteLLMPolicy("test", 0.002)
    assert policy.plan(["book"]).intent == "book"
    with pytest.raises(BudgetExceeded):
        policy.plan(["book"])
    assert len(calls) == 1
    assert calls[0]["tool_choice"]["function"]["name"] == "choose_intent"
    with pytest.raises(ValueError):
        policy.plan([])
    judge = LiteLLMJudge("test", 0.002)
    assert judge.score("Choose a time.").clarity == 5
    with pytest.raises(ValueError):
        judge.score("Choose a time.")
    with pytest.raises(ValueError):
        judge.score("")

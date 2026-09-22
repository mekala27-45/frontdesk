import json

import pytest

from scripts.showcase import NAMES, document, publish


def evidence(tmp_path):
    snapshot = tmp_path / "artifacts/database.json"
    snapshot.parent.mkdir()
    snapshot.write_text('{"synthetic":true}')
    values = dict.fromkeys(NAMES, "{}")
    values["redteam"] = json.dumps(
        {
            "scenarios": [
                {
                    "clinic_id": "test-clinic",
                    "conversation_id": "test-conversation",
                    "replay": [
                        {
                            "content_summary": "confirmation",
                            "tool_calls": [
                                {
                                    "name": "book_slot",
                                    "arguments": {
                                        "patient_wa_id": "synthetic-recipient",
                                        "patient_name": "Demo visitor",
                                        "slot_id": "test-slot",
                                    },
                                    "result": {"ok": True, "code": "ok", "ids": ["test-booking"]},
                                }
                            ],
                        }
                    ],
                }
            ]
        }
    )
    return values, snapshot


def test_showcase_clean_tampered_empty(tmp_path):
    values, snapshot = evidence(tmp_path)
    assert publish(tmp_path, values, True) == []
    assert publish(tmp_path, values) == []
    target = tmp_path / "web/public/evidence.json"
    target.write_text(target.read_text().replace('"ok": true', '"ok": false'))
    assert publish(tmp_path, values) == ["web/public/evidence.json"]
    with pytest.raises(ValueError, match="Incomplete"):
        document({}, snapshot)
    values["redteam"] = '{"scenarios": []}'
    with pytest.raises(ValueError, match="Empty"):
        document(values, snapshot)


def test_showcase_excludes_recipient_and_tracks_snapshot(tmp_path):
    values, snapshot = evidence(tmp_path)
    original = document(values, snapshot)
    assert "patient_wa_id" not in original and "patient_name" not in original
    assert "test-conversation" not in original and "test-slot" in original
    assert "synthetic-recipient" in values["redteam"]  # Does not mutate source evidence.
    snapshot.write_text('{"synthetic":false}')
    assert document(values, snapshot) != original

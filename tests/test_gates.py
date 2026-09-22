import pytest

from scripts.check_no_em_dash import violations
from scripts.check_published_numbers import render


def test_punctuation_clean_violation_empty(tmp_path):
    path = tmp_path / "template.json"
    path.write_text('{"reply":"Hello"}')
    assert not violations(tmp_path, ["template.json"])
    path.write_text(chr(0x2014), encoding="utf-8")
    assert violations(tmp_path, ["template.json"]) == ["template.json"]
    with pytest.raises(ValueError):
        violations(tmp_path, [])


def test_renderer_clean_violation_empty(tmp_path):
    directory = tmp_path / "docs/templates"
    directory.mkdir(parents=True)
    (directory / "README.md").write_text("Measured $count")
    assert not render(tmp_path, {"count": "1"}, True)
    assert not render(tmp_path, {"count": "1"})
    (tmp_path / "README.md").write_text("Measured 1 plus an invented claim")
    assert render(tmp_path, {"count": "1"}) == ["README.md"]
    with pytest.raises(ValueError):
        render(tmp_path, {})
    with pytest.raises(ValueError):
        render(tmp_path / "missing", {"count": "1"})


def test_timezone_gate_clean_violation_empty(tmp_path):
    from scripts.check_timezones import violations

    source = tmp_path / "clock.py"
    source.write_text("from datetime import datetime, UTC\nx=datetime.now(UTC)\n")
    assert not violations([source])
    source.write_text("from datetime import datetime\nx=datetime.now()\n")
    assert violations([source])
    with pytest.raises(ValueError):
        violations([])


def test_uuid7_is_monotonic():
    from uuid import UUID

    from frontdesk_core.contracts import uuid7

    values = [UUID(uuid7()) for _ in range(100)]
    assert values == sorted(values) and all(v.version == 7 for v in values)

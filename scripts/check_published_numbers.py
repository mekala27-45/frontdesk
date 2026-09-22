"""Whole-document renderer. Evidence is selected from the database, never prose."""

import json
from pathlib import Path
from string import Template

from sqlalchemy import text
from sqlmodel import Session

ROOT = Path(__file__).resolve().parents[1]


def manifest(session: Session) -> dict[str, str]:
    rows = session.execute(text("SELECT name, value FROM evidence ORDER BY name")).all()
    if not rows:
        raise ValueError("No measured evidence")
    data = dict(rows)
    required = {"concurrency", "tenant", "dst", "idempotency", "redteam", "quality"}
    if not required.issubset(data):
        raise ValueError("Incomplete measured evidence")
    values = {name: json.dumps(value, indent=2, sort_keys=True) for name, value in rows}
    categories = data["redteam"]["categories"]
    values["category_table"] = "| Category | Passed | Total |\n| --- | ---: | ---: |\n" + "\n".join(f"| {name} | {group['passed']} | {group['total']} |" for name, group in categories.items())
    scenarios = data["redteam"]["scenarios"]
    # Re-read the source audit rows; a missing or altered replay invalidates evidence.
    for scenario in scenarios:
        stored = session.execute(text("SELECT content_summary, tool_calls FROM message WHERE clinic_id=:clinic AND conversation_id=:conversation AND direction='inbound' ORDER BY created_at, id"), {"clinic": scenario["clinic_id"], "conversation": scenario["conversation_id"]}).all()
        actual = [{"content_summary":summary,"tool_calls":calls} for summary,calls in stored]
        if actual != scenario["replay"]:
            raise ValueError("Audit source differs from scored evidence: " + scenario["id"])
    values["scorecard"] = "| Scenario | Task | Safety | Confirmation | Turns | Replay |\n| --- | --- | --- | --- | ---: | --- |\n" + "\n".join(f"| {s['id']} | {s['task_correct']} | {s['safety_correct']} | {s['no_hallucinated_confirm']} | {s['resolution_turns']} | [Audit](docs/replays/{s['id']}.md) |" for s in scenarios)
    values["redteam_total"] = str(len(scenarios))
    values["redteam_passed"] = str(sum(s["passed"] for s in scenarios))
    values["coverage_percent"] = str(data["quality"]["coverage_percent"])
    return values


def render(root: Path, values: dict[str, str], write: bool = False) -> list[str]:
    templates = sorted((root / "docs/templates").glob("*.md"))
    if not templates or not values:
        raise ValueError("Empty claim gate input")
    errors = []
    for source in templates:
        result = Template(source.read_text(encoding="utf-8")).substitute(values)
        target = root / source.name
        if write:
            target.write_text(result, encoding="utf-8")
        elif not target.exists() or target.read_text(encoding="utf-8") != result:
            errors.append(source.name)
    return errors


if __name__ == "__main__":
    import sys

    from frontdesk_core.db import engine

    with Session(engine()) as session:
        values = manifest(session)
    if render(ROOT, values, "--write" in sys.argv):
        raise SystemExit("Published documents differ from database evidence")

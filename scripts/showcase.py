"""Publish a bounded, deterministic view of the verified PostgreSQL evidence."""

import hashlib
import json
from pathlib import Path

from scripts.check_published_numbers import ROOT

NAMES = ("concurrency", "dst", "tenant", "idempotency", "redteam", "quality")


def document(values: dict[str, str], snapshot: Path) -> str:
    if not snapshot.is_file() or not all(name in values for name in NAMES):
        raise ValueError("Incomplete showcase evidence")
    data = {name: json.loads(values[name]) for name in NAMES}
    scenarios = data["redteam"]["scenarios"]
    if not scenarios or any(not s["replay"] for s in scenarios):
        raise ValueError("Empty showcase replay")
    # Deliberately exclude operational tables and test-only cost reservations.
    for scenario in scenarios:
        scenario.pop("clinic_id", None)
        scenario.pop("conversation_id", None)
        for turn in scenario["replay"]:
            for call in turn["tool_calls"]:
                call["arguments"].pop("patient_wa_id", None)
                call["arguments"].pop("patient_name", None)
    data["provenance"] = {
        "schema_version": 1,
        "mode": "recorded_test_evidence",
        "snapshot": "artifacts/database.json",
        "snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        "verification": "PostgreSQL audit rows and deterministic rescoring",
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def publish(root: Path, values: dict[str, str], write: bool = False) -> list[str]:
    result = document(values, root / "artifacts/database.json")
    target = root / "web/public/evidence.json"
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result, encoding="utf-8", newline="\n")
    elif not target.is_file() or target.read_text(encoding="utf-8") != result:
        return ["web/public/evidence.json"]
    return []


if __name__ == "__main__":
    import sys

    from frontdesk_core.db import engine
    from sqlmodel import Session

    from scripts.check_published_numbers import manifest

    with Session(engine()) as session:
        verified = manifest(session)
    if publish(ROOT, verified, "--write" in sys.argv):
        raise SystemExit("Showcase differs from verified database evidence")
    print("Showcase matches verified database evidence.")

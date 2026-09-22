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
    return {name: json.dumps(value, indent=2, sort_keys=True) for name, value in rows}


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

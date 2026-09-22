"""Transfer synthetic relational evidence without copying credentials."""
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import DateTime, Engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import SQLModel
from frontdesk_core import models  # noqa: F401
from frontdesk_core.db import engine

def export_snapshot(db: Engine, target: Path) -> None:
    snapshot={}
    with db.connect() as conn:
        for table in SQLModel.metadata.sorted_tables:
            snapshot[table.name]=[dict(row) for row in conn.execute(select(table)).mappings()]
    target.write_text(json.dumps(snapshot,default=lambda v:v.isoformat(),separators=(",",":")),encoding="utf-8")

def restore_snapshot(db: Engine, source: Path) -> None:
    data=json.loads(source.read_text(encoding="utf-8"))
    if not data or not data.get("evidence"):
        raise ValueError("Empty evidence snapshot")
    with db.begin() as conn:
        for table in SQLModel.metadata.sorted_tables:
            for record in data.get(table.name,[]):
                for column in table.columns:
                    if isinstance(column.type,DateTime) and record.get(column.name):
                        record[column.name]=datetime.fromisoformat(record[column.name])
                statement=insert(table).values(**record)
                if table.name=="evidence":
                    statement=statement.on_conflict_do_update(index_elements=["name"],set_={"value":record["value"]})
                else:
                    statement=statement.on_conflict_do_nothing()
                conn.execute(statement)

if __name__=="__main__":
    restore_snapshot(engine(),Path("artifacts/database.json"))


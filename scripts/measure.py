"""Run fresh checks, persist evidence, render complete published documents."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from sqlmodel import Session
from frontdesk_core.contracts import now
from frontdesk_core.db import engine
from frontdesk_core.models import Evidence
from scripts.evidence_db import restore_snapshot
from scripts.check_published_numbers import ROOT, manifest, render

def main() -> None:
    if not shutil.which("docker") or subprocess.run(["docker","info"],capture_output=True).returncode:
        raise SystemExit("Measurement requires a running Docker daemon; no skip accepted.")
    subprocess.run([sys.executable,"-m","pytest","--cov","--cov-report=json:artifacts/coverage.json","-q"],env={**os.environ,"PUBLISH_EVIDENCE":"1"},check=True)
    database=engine()
    restore_snapshot(database,Path("artifacts/database.json"))
    coverage=json.loads(Path("artifacts/coverage.json").read_text())
    with Session(database) as session:
        quality={"coverage_percent":round(coverage["totals"]["percent_covered"],2),"covered_statements":coverage["totals"]["covered_lines"],"total_statements":coverage["totals"]["num_statements"],"measured_at":now().isoformat()}
        session.merge(Evidence(name="quality",value=quality))
        session.commit()
        values=manifest(session)
    render(ROOT,values,True)
    snapshot_path=Path("artifacts/database.json")
    snapshot=json.loads(snapshot_path.read_text())
    snapshot["evidence"].append({"name":"quality","value":quality})
    snapshot_path.write_text(json.dumps(snapshot,separators=(",",":")))
    replay_dir=Path("docs/replays")
    replay_dir.mkdir(exist_ok=True)
    for scenario in json.loads(values["redteam"])["scenarios"]:
        (replay_dir/(scenario["id"]+".md")).write_text("# "+scenario["id"]+"\n\nGenerated logistics summaries only. Raw input is not retained.\n\n~~~json\n"+json.dumps(scenario["replay"],indent=2)+"\n~~~\n",encoding="utf-8")
    print("Measured documents rendered from PostgreSQL evidence.")

if __name__=="__main__":
    main()

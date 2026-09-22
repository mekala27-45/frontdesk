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
from scripts.evidence_db import export_snapshot, restore_snapshot
from scripts.check_published_numbers import ROOT, manifest, render

def main() -> None:
    if not shutil.which("docker") or subprocess.run(["docker","info"],capture_output=True).returncode:
        raise SystemExit("Measurement requires a running Docker daemon; no skip accepted.")
    subprocess.run([sys.executable,"-m","pytest","--cov","--cov-report=json:artifacts/coverage.json","-q"],env={**os.environ,"PUBLISH_EVIDENCE":"1"},check=True)
    database=engine()
    restore_snapshot(database,Path("artifacts/database.json"))
    coverage=json.loads(Path("artifacts/coverage.json").read_text())
    with Session(database) as session:
        session.merge(Evidence(name="quality",value={"coverage_percent":round(coverage["totals"]["percent_covered"],2),"covered_statements":coverage["totals"]["covered_lines"],"total_statements":coverage["totals"]["num_statements"],"measured_at":now().isoformat()}))
        session.commit()
        values=manifest(session)
    render(ROOT,values,True)
    export_snapshot(database,Path("artifacts/database.json"))
    print("Measured documents rendered from PostgreSQL evidence.")

if __name__=="__main__":
    main()


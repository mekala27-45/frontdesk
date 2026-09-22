import json
import os
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

import pytest
from frontdesk_core.contracts import now
from frontdesk_core.db import engine
from frontdesk_core.models import (
    Clinic,
    Conversation,
    Evidence,
    Provider,
    ProviderService,
    Service,
    Slot,
)
from sqlmodel import Session, SQLModel, select
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def db():
    if not shutil.which("docker"):
        pytest.skip("Missing external dependency: Docker executable")
    probe = subprocess.run(["docker", "info"], capture_output=True)
    if probe.returncode:
        pytest.skip("Missing external dependency: running Docker daemon")
    with PostgresContainer("postgres:17-alpine", driver="psycopg") as postgres:
        url = postgres.get_connection_url().replace("localhost", "127.0.0.1")
        database = engine(url)
        SQLModel.metadata.create_all(database)
        yield database
        if os.getenv("PUBLISH_EVIDENCE") == "1":
            with Session(database) as session:
                rows = session.exec(select(Evidence)).all()
                data = {r.name: r.value for r in rows}
            Path("artifacts").mkdir(exist_ok=True)
            Path("artifacts/measured.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
            from scripts.evidence_db import export_snapshot

            export_snapshot(database, Path("artifacts/database.json"))
        database.dispose()


def make_clinic(session, phone=None):
    from frontdesk_core.contracts import uuid7

    clinic = Clinic(
        name="Fictional test clinic",
        whatsapp_phone_number_id=phone or uuid7(),
        business_hours={str(i): [0, 24] for i in range(7)},
    )
    session.add(clinic)
    session.flush()
    provider = Provider(clinic_id=clinic.id, name="Avery Lane")
    services = [
        Service(clinic_id=clinic.id, name=name)
        for name in ["Welcome visit", "Routine visit", "Extended visit"]
    ]
    session.add(provider)
    for service in services:
        session.add(service)
    session.flush()
    slots = []
    for i, service in enumerate(services):
        session.add(
            ProviderService(clinic_id=clinic.id, provider_id=provider.id, service_id=service.id)
        )
        for j in range(3):
            start = (now() + timedelta(days=2, hours=i * 3 + j)).replace(second=0, microsecond=0)
            slot = Slot(
                clinic_id=clinic.id,
                provider_id=provider.id,
                service_id=service.id,
                starts_at=start,
                ends_at=start + timedelta(minutes=30),
            )
            session.add(slot)
            slots.append(slot)
    convo = Conversation(clinic_id=clinic.id, wa_id="15550001111")
    session.add(convo)
    session.commit()
    for row in [clinic, provider, *services, *slots, convo]:
        session.refresh(row)
        session.expunge(row)
    return clinic, provider, services, slots, convo


@pytest.fixture
def clinic(db):
    with Session(db) as session:
        return make_clinic(session)


def evidence(db, name, value):
    with Session(db) as session:
        row = session.get(Evidence, name) or Evidence(name=name, value={})
        row.value = {**value, "measured_at": now().isoformat()}
        session.add(row)
        session.commit()

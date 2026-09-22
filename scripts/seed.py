from frontdesk_core.db import engine
from frontdesk_core.models import Clinic, Provider, ProviderService, Service
from frontdesk_scheduling.slots import generate
from sqlmodel import Session, select


def seed(
    session: Session, phone: str = "demo-phone", name: str = "Ridgeview Family and Wellness Clinic"
) -> Clinic:
    clinic = session.exec(select(Clinic).where(Clinic.whatsapp_phone_number_id == phone)).first()
    if clinic:
        generate(session, clinic.id)
        return clinic
    clinic = Clinic(name=name, whatsapp_phone_number_id=phone)
    session.add(clinic)
    session.flush()
    services = [
        Service(clinic_id=clinic.id, name=name, duration_minutes=duration, buffer_minutes=buffer)
        for name, duration, buffer in [
            ("Welcome visit", 30, 0),
            ("Routine visit", 20, 10),
            ("Extended visit", 45, 15),
        ]
    ]
    for service in services:
        session.add(service)
    for name in ["Avery Lane", "Morgan Reed", "Taylor Quinn"]:
        provider = Provider(clinic_id=clinic.id, name=name)
        session.add(provider)
        session.flush()
        for service in services:
            session.add(
                ProviderService(clinic_id=clinic.id, provider_id=provider.id, service_id=service.id)
            )
    session.flush()
    generate(session, clinic.id)
    return clinic


if __name__ == "__main__":
    with Session(engine()) as session:
        clinic = seed(session)
        session.commit()
        print(clinic.id)

import re

from frontdesk_core.contracts import Category

EMERGENCY = re.compile(
    r"chest pain|can.?t breathe|cannot breathe|severe bleeding|suicid|kill myself|end my life|overdose|unconscious|not breathing",
    re.I,
)
INJECTION = re.compile(
    r"ignore|system prompt|developer says|override|jailbreak|pretend|bypass|skip verification|you are now|reveal|booked without|just (say|tell)|forget (your|all)|act as",
    re.I,
)
MEDICAL = re.compile(
    r"symptom|diagnos|pain|fever|rash|bleed|sick|cough|dizz|pregnan|condition|medical advice|treat|disease|blood|cancer|diabet",
    re.I,
)
PRESCRIPTION = re.compile(r"prescri|medicat|dosage|dose|antibiotic|refill|pill|drug", re.I)
OTHER = re.compile(
    r"someone else|another patient|other patient|my (wife|husband|friend|mother|father)|their booking|all patients|under.*name|phone number",
    re.I,
)


def classify_safety(body: str) -> Category | None:
    if EMERGENCY.search(body):
        return "emergency"
    if INJECTION.search(body):
        return "unrelated"
    if OTHER.search(body):
        return "other_patient_data"
    if PRESCRIPTION.search(body):
        return "prescription_question"
    if MEDICAL.search(body):
        return "medical_question"
    if re.search(r"insurance|price|cost|coverage|copay", body, re.I):
        return "pricing_or_insurance_detail"
    return None


REFUSALS = {
    "medical_question": "I handle appointment logistics only. Please contact a qualified clinician for medical questions.",
    "prescription_question": "I cannot help with prescriptions. Please contact your clinician or pharmacist.",
    "other_patient_data": "I can only manage bookings belonging to this conversation.",
    "pricing_or_insurance_detail": "The front desk can help with pricing and insurance. Choose Talk to a person.",
    "unrelated": "I can help with booking, rescheduling, or cancelling an appointment.",
    "emergency": "If you may be in immediate danger, call your local emergency services now. In the US, call 911. For a suicide or mental health crisis in the US, call or text 988. I have also alerted the front desk; do not wait for a reply.",
}

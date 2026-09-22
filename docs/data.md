# Data boundary

No clinical data is persisted or logged. The fictional business, service names, providers, test callers and appointments are synthetic. No real patient data was imported.

Allowed storage: clinic configuration, provider/service identity, slot timestamps, booking reference and status, caller routing identifier, a fixed demo alias, generated logistics summary, typed tool arguments/results and delivery status. Phone routing IDs are required for WhatsApp delivery and are masked to the final digits by the log processor.

Disallowed storage: raw inbound body, symptoms, diagnosis, medication, medical condition, arbitrary profile names, arbitrary operator notes and provider error bodies. The schema has no clinical fields. JSON fields are populated by application-generated frames and typed tools, never copied from inbound content.

The browser displays input transiently to conduct the chat. Reloading drops its session. Server-side replays show canonical summaries rather than raw text. Fixtures contain invented adversarial prompts solely to test refusal; they are not patient records.

Run only with invented content. TLS termination, vendor contracts, encryption key management, access audit policies, retention and deletion procedures, abuse protection, a legal/compliance review and applicable BAAs would require separate work before any real clinical deployment. This project makes no HIPAA compliance claim.


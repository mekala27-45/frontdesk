# Build series log

## Day 4: Frontdesk

Built a fictional clinic logistics agent with a shared WhatsApp/simulator ingestion function, persisted slot filling, transactional provider and slot locks, idempotent webhook processing, structured refusals, a deterministic emergency override, calendar adapters, a signed reminder endpoint and a static operations console.

Reusable: message-id deduplication plus a transactional outbox; provider locks for overlapping scarce-resource claims; deterministic refusal tools; an emergency override before any optional model call; an evidence snapshot whose source rows are rechecked by a whole-document renderer.

Finding: a claim gate caught unstable replay ordering that the scenario assertions alone missed. Outbound HTTP delivery needs an explicit ambiguous state because a database cannot atomically commit a remote side effect.

Measured results are linked in RESULTS.md rather than repeated here. The source repository and CI are published. Live API/Pages hosting, provider round trips and custom template approval remain pending. The demo GIF records the local browser simulator, not an actual WhatsApp device.


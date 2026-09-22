# Runbook

Use this for local verification, deployment preparation and delivery recovery. All data must be fictional.

## Local operation

Start Postgres with docker compose up -d, run uv sync --frozen, uv run alembic upgrade head and uv run python -m scripts.seed. Start uvicorn on port 8001 with --no-access-log, then npm ci and npm run dev inside web. The simulator obtains a signed temporary identity from the API. Enter the local OPS_TOKEN in the console.

Use GET /health for reachability and database access. The endpoint reports dev or meta transport. The seed operation can run again to extend the scheduling horizon.

## Reproduce measurements

Run uv run python -m scripts.measure. It probes Docker, executes tests, stores fresh evidence, imports the relational snapshot into local Postgres and renders README/RESULTS. The duration may differ from the committed result. The independent gate runs with uv run python -m scripts.check_published_numbers.

To verify committed claims in a fresh database, migrate, run uv run python -m scripts.evidence_db and then run the claim gate. The imported evidence is synthetic. Do not import evaluation fixtures into a database connected to live providers.

## Deployment status

Live application deployment is blocked by an API host account and a Neon connection string. The GitHub repository is published and its CI passed using the authenticated browser and existing Git credentials. Fly.io explicitly has [no free tier](https://fly.io/docs/about/cost-management/). The free-only requirement therefore conflicts with the requested host. No funded service was created.

The Fly configuration and Docker image are ready for account-specific configuration. Set the app name in fly.toml, create the Postgres database, configure secrets, and deploy only after choosing an acceptable hosting cost. Change every local default secret. Use a restricted CORS origin for the published Pages URL. Set database connection pooling appropriate to the hosted plan; the benchmark pool is intentionally generous.

GitHub Pages requires NEXT_PUBLIC_API_URL and NEXT_PUBLIC_BASE_PATH repository variables. Never put an ops token or Meta token into the static bundle. The reminders workflow needs FRONTDESK_API_URL and REMINDER_SECRET as secrets and ENABLE_REMINDERS=true as a variable.

The release workflow requires a pushed version tag. A pushed annotated version tag creates the source release. Repository description, topics, profile pin and social preview are configured. The local demo GIF must not be described as a real-device WhatsApp recording.

## Real provider setup

Meta: set the app secret, verify token, access token and phone identity. Add the allowed test recipient and confirm the callback challenge. Seed a separate fictional clinic using scripts.seed.seed(session, phone=the_phone_id). Run a test message from the allowed device and verify a single booking and outbound reply. Keep the public simulator on its separate demo-phone identity.

Google: enable Calendar API, create a dedicated demo calendar, give the service account writer access, and set GOOGLE_CALENDAR_ID and GOOGLE_APPLICATION_CREDENTIALS. Event descriptions contain only booking references, not caller identities. Calendar failures retain pending work for the next webhook/reminder run.

Custom reminder template: none was submitted or approved. The hello_world sample is not an appointment reminder. Replace template_message with an approved utility template and its approved parameters, then run the transport tests and a real test-device round trip.

## Delivery and handoff recovery

Inspect outbox rows by clinic. Sent means a provider request returned successfully, not that a person read it. Unknown or sending needs reconciliation with the provider before retry. Automatic retries of ambiguous sends are deliberately disabled.

Calendar jobs remain pending after a failed call and are safe to retry because event IDs are stable. The scheduled endpoint also processes pending calendar jobs.

Open handoffs appear in the console. Inspect the generated summaries, then mark resolved after a human has handled the request through the appropriate channel. The demo does not send arbitrary operator messages.

For deployment rollback, restore the previous immutable container release and retain the database. Do not downgrade the initial migration on a database containing work: it drops the schema. Take a database backup before schema changes.

## Known operational gaps

No real patient use, per-operator accounts, durable public rate limiting, language localization, compliance program or guaranteed scheduler latency. Default database pool size is suitable for a local benchmark, and must be reduced for small hosted database limits.


# frontdesk

**No clinical data is persisted or logged.** This fictional clinic demo handles appointment logistics only. Incoming text is transient; durable conversations contain generated summaries, structured tool calls, and a fixed demo visitor alias.

**A WhatsApp booking agent built around the hard parts: competing claims, webhook retries, and auditable safety decisions.** FastAPI, PostgreSQL, typed tools, and a Next.js evidence explorer.

[![CI](https://github.com/mekala27-45/frontdesk/actions/workflows/ci.yml/badge.svg)](https://github.com/mekala27-45/frontdesk/actions/workflows/ci.yml)
[![Pages](https://github.com/mekala27-45/frontdesk/actions/workflows/pages.yml/badge.svg)](https://github.com/mekala27-45/frontdesk/actions/workflows/pages.yml)

**[Open the public evidence explorer](https://mekala27-45.github.io/frontdesk/)** · [Architecture](ARCHITECTURE.md) · [Measured results](RESULTS.md) · [Case study](docs/case-study.md)

No setup or login needed. Explore recorded test results, search scenarios, step through persisted tool traces, and compare expected calls with observed decisions. The public site serves archived synthetic evidence. The full booking simulator and operations console run locally against the real API.

![Public evidence explorer](docs/evidence-explorer.png)

## Review path

| Engineering question | Inspect the proof | Read the implementation |
| --- | --- | --- |
| Can competing requests double-book? | [Concurrency test](tests/test_scheduling.py) | [Provider and slot locks](packages/scheduling/src/frontdesk_scheduling/engine.py) |
| What happens after a retry or restart? | [Webhook tests](tests/test_webhook.py) | [Durable conversation engine](packages/agent/src/frontdesk_agent/engine.py) |
| Does the agent actually refuse unsafe requests? | [Scenario explorer](https://mekala27-45.github.io/frontdesk/evidence/#scenario=34-medical) | [Safety rules](packages/agent/src/frontdesk_agent/safety.py) and [deterministic scorer](redteam/score.py) |
| Can a tool cross a tenant boundary? | [Tenant isolation tests](tests/test_tenants.py) | [Scoped tool dispatch](packages/agent/src/frontdesk_agent/tools.py) |
| Can the published numbers drift? | [Database claim gate](scripts/check_published_numbers.py) | [Public evidence exporter](scripts/showcase.py) |

## The scheduling proof

Measured against real Postgres, through concurrent HTTP requests to the FastAPI application:

<details>
<summary>Inspect the measured concurrency record</summary>

~~~json
$concurrency
~~~

</details>

The connection pool is warmed before timing. This is a local ASGI benchmark, not an internet latency measurement. [Full results](RESULTS.md) include tenant isolation, daylight saving transitions, duplicate delivery and every scenario.

<details>
<summary>Watch the local booking simulator walkthrough</summary>

![Recorded local simulator walkthrough](docs/demo.gif)

</details>

## Try it locally

~~~sh
uv sync --frozen
docker compose up -d
uv run alembic upgrade head
uv run python -m scripts.seed
uv run uvicorn frontdesk_api.app:app --port 8001 --no-access-log
~~~

In another terminal:

~~~sh
cd web
npm ci
npm run dev
~~~

Open the [simulator](http://localhost:3000/simulator/) or [operations console](http://localhost:3000/console/). The local console token is in [.env.example](.env.example). Keep the API bound to loopback until deployment secrets are configured.

The default path uses the deterministic offline policy, DevTransport and NullCalendarAdapter. No Meta, model, or Google credentials are required. The simulator submits Meta-shaped payloads to the same ingestion function as the signed webhook.

## What was measured

The deterministic suite passed $redteam_passed of $redteam_total scenarios. Application statement coverage is $coverage_percent percent.

$category_table

## The interesting decision

Refusal is a named tool call. Safety scoring queries persisted tool calls instead of asking a model to judge a reply. A model judging its own family's safety behavior creates a conflict of interest; a missing required tool call is a fact.

The emergency override runs before the optional model policy in every conversation state. Booking confirmation requires a successful scheduling transaction. Provider locks prevent overlap between different service types, and ownership checks apply inside each tool.

## Deployment state and limits

The public portfolio is a static GitHub Pages evidence explorer with no API credentials or live booking endpoint. Its JSON is rendered from verified PostgreSQL evidence, and publication waits for successful CI. The local simulator and API are verified. A live Meta webhook round trip, Google Calendar delivery and a real-device recording have **not** been verified. No credentialed provider calls were made. No custom reminder template was submitted or approved. The default template is Meta's sample and is only a transport demonstration, not a useful appointment reminder.

An always-on public API is optional for this portfolio. Fly.io no longer offers a free tier, so no funded backend was provisioned. See the [showcase publication guide](docs/showcase.md) or the [API deployment runbook](docs/runbook.md).

English only. Rule-based interpretation is deliberately limited. No unrestricted medical conversation, payments, or production readiness claim. The console uses a demo token, not individual operator authentication. There is no HIPAA compliance claim.

Meta can accept a message before a connection fails. Ambiguous sends are marked for human review instead of automatic retry. This avoids duplicate send attempts at the cost of possible missed delivery. [Architecture and guarantees](ARCHITECTURE.md).

## Reproduce and contribute

~~~sh
uv run python -m scripts.measure
uv run python -m scripts.check_published_numbers
uv run python -m scripts.showcase
uv run python -m scripts.check_no_em_dash
uv run python -m scripts.check_timezones
uv run ruff check .
uv run mypy
~~~

Measurement requires Docker and refuses silent skipping. The claim gate reloads the relational evidence snapshot, checks source audit rows, and compares whole rendered documents. Edit templates rather than published results. [Contributing](CONTRIBUTING.md) · [Data boundaries](docs/data.md) · [Safety](docs/safety.md) · [WhatsApp integration](docs/whatsapp-integration.md).


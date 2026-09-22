# Measured results

These are local measurements from real Postgres containers. They do not establish live provider delivery or production readiness.

## Concurrent slot claims

~~~json
$concurrency
~~~

Requests use an asynchronous HTTP ASGI client. The timer excludes container startup, migration, seed data and connection pool warmup. The database is real; network round trip latency to a public API is not measured.

## Tenant isolation

~~~json
$tenant
~~~

The suite explicitly rejects foreign resources through each tool, including refusal and handoff tools using a foreign conversation. A separate gate test proves clean, deliberate-violation and empty-input behavior.

## Daylight saving transitions

~~~json
$dst
~~~

The test window starts at local midnight and ends in the local early morning. Advancing in UTC excludes nonexistent spring times and preserves distinct repeated fall times.

## Webhook replay and restart recovery

~~~json
$idempotency
~~~

Booking state and the outbox are committed together. Duplicate delivery does not execute tools or send another reply. The test reconstructs the application between selection and confirmation.

## Red team categories

$category_table

## Full scenario scorecard

Safety is deterministic: the scorer checks named tool calls in persisted audit rows. A model grading its own family's safety is a conflict of interest, and a wrong tool call is a fact, not an opinion. Optional model quality scoring is secondary and was not run against a live provider.

$scorecard

Audit links contain generated summaries and structured tool calls, not raw inbound clinical text. The console also offers archived scenario replay when the test database is no longer running.

## Coverage

~~~json
$quality
~~~

## Limits and unmeasured work

- The public GitHub Pages explorer serves recorded test evidence. No public API, live Meta device conversation, or live Google Calendar round trip was verified.
- The sample template demonstrates formatting and dispatch. A custom utility reminder remains unsubmitted and unapproved.
- GitHub scheduled jobs can be delayed. The reminder query catches due work, but scheduling is not a real-time guarantee.
- The rule-based emergency vocabulary is finite and can miss unfamiliar wording. This is a fictional logistics demo, not emergency triage.
- A provider lock can reject simultaneous non-overlapping claims for that provider; callers can retry through a fresh choice. The design favors bounded lock contention and correctness.
- External message delivery cannot be atomically committed with Postgres. Sending/unknown outbox entries need operator reconciliation.
- Slot utilization counts service candidates, which can overlap. It is not a count of independent provider capacity.
- There is no public abuse protection, per-operator identity, or comprehensive retention scheduler. Do not use real patient information.

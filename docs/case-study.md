# Frontdesk: correctness before conversation

A fictional clinic needs appointments to survive retries, restarts and simultaneous demand. The interesting engineering decision was to make refusals explicit tools and safety scoring deterministic.

## What the implementation proves

A shared ingestion function handles signed Meta webhooks and synthetic browser messages. A conversation advisory lock and message uniqueness constraint make retries safe. Provider and slot row locks protect scarce capacity, including overlapping service types. Slot selection is persisted before confirmation so a process restart does not forget what the visitor chose.

The results come from real Postgres containers. The published artifacts preserve synthetic relational audit rows and independently re-score the decisions. Whole-document rendering rejects prose that differs from measured evidence.

## The decision worth discussing

A statement such as "the prompt tells the model not to give medical advice" is difficult to audit. Frontdesk instead records refuse_out_of_scope or escalate_to_human in its tool log. A missing refusal fails a deterministic assertion. A secondary model can score tone, but it has no vote in the safety gate.

The optional planner only receives closed-vocabulary logistics cues. Raw text does not leave the server for model inference and is never persisted. A fixed visitor alias avoids collecting names that could contain accidental clinical content.

## Failure handling

A competing slot claim gets a clean rejection. A failed reschedule leaves the original booking intact. A failed calendar call leaves retryable work with a stable event identity. An ambiguous Meta send remains visible for operator review because exactly-once delivery cannot be honestly promised across a database and a remote HTTP service.

## What remains unproven

The browser GIF uses the real local engine with DevTransport. Public hosting, a real-device WhatsApp recording, Google Calendar delivery and a custom approved reminder template remain unverified. Fly's current paid hosting conflicts with the original free-only brief.

See [measured results](../RESULTS.md), [architecture](../ARCHITECTURE.md) and the [runbook](runbook.md).


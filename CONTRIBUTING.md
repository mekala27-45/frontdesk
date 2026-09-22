# Contributing

Use Python 3.12, uv, Node and Docker. Run the quick start in README, then:

~~~sh
uv run ruff check .
uv run mypy
uv run python -m pytest --cov
uv run python -m scripts.check_no_em_dash
uv run python -m scripts.check_timezones
cd web
npm run typecheck
npm run build
npm audit
~~~

Tests start a disposable Postgres container. External tests probe Docker and name the missing dependency when unavailable; CI checks Docker before pytest so skipped integration tests cannot appear green.

Use synthetic identifiers only. Never add patient data or logs of request bodies. Response templates, fixtures and docs must pass the punctuation gate. New gates need clean, deliberate-violation and empty-input tests.

Published documents are generated. Change docs/templates, run scripts.measure, and commit the measured snapshot together with the rendered documents. Timing is machine-specific; do not edit measured values manually.

Conventional commits describe meaningful checkpoints. Keep optional model spend opt-in. No payment or real patient workflows belong in this repository.


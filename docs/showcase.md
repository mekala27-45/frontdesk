# Public portfolio

[Open frontdesk](https://mekala27-45.github.io/frontdesk/) to explore recorded synthetic test evidence. This static site has no live booking API, credentials, patient input, or operating costs from backend providers.

## What a reviewer can inspect

- Measured concurrency outcomes, tenant checks, retry behavior and daylight saving results.
- Searchable scenarios with category filters and direct links to individual traces.
- Step-by-step replay of generated summaries, typed arguments, and tool results.
- Expected calls compared with the turns revealed so far. The full verdict comes from the Python deterministic scorer.
- Architecture decisions linked to source files and tests, with explicit tradeoffs.
- Downloadable evidence and a SHA-256 digest identifying the archived relational snapshot.

The concurrency scenario replays show the winning caller's audit, as selected by the test. The overview's claim grid groups measured outcomes by status; it does not invent individual request timings or arrival order. The suite covers scripted cases and finite English patterns, not every possible unsafe message.

## Publication

Repository Settings > Pages uses GitHub Actions as its source. The Pages workflow starts after CI succeeds on main, checks out that exact tested revision, restores the archived snapshot into disposable PostgreSQL, and runs both publication gates before building and deploying. It can also be dispatched manually; a manual run still validates the snapshot and generated files.

The workflow sets NEXT_PUBLIC_SHOWCASE=true and NEXT_PUBLIC_BASE_PATH from the repository name. The public simulator and console routes explain the local setup instead of exposing nonfunctional connection forms. A normal local build retains the live simulator and console.

For a local portfolio preview, set those environment variables before npm run build in web, then serve web/out under the configured base path. No database is needed to browse the committed evidence. PostgreSQL is required to regenerate or verify it.

## Updating evidence

With local PostgreSQL migrated, run:

```sh
uv run python -m scripts.measure
uv run python -m scripts.check_published_numbers
uv run python -m scripts.showcase
```

The measurement command updates both documents and web/public/evidence.json. To regenerate only the public file from already verified database evidence, use uv run python -m scripts.showcase --write. Never edit published statistics manually.

## Verification and rollback

Before publication, check the Python tests, document gate, public JSON gate, TypeScript checks, production export, and desktop/mobile layout. After deployment, verify the landing page, direct scenario link, search, turn controls, download link, and local-only route notices. Confirm the deployed evidence matches the committed JSON.

If routes or assets fail, redeploy the last known good Pages artifact or revert the showcase commit on main and let CI republish. The static site has no database migration and changes no booking data.

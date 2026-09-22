setup:
	uv sync --frozen
	docker compose up -d
	uv run alembic upgrade head
	uv run python -m scripts.seed

serve:
	uv run uvicorn frontdesk_api.app:app --port 8001 --no-access-log

test:
	uv run python -m pytest --cov

check:
	uv run ruff check .
	uv run mypy
	uv run python -m scripts.check_no_em_dash
	uv run python -m scripts.check_timezones
	uv run python -m scripts.check_published_numbers

measure:
	uv run python -m scripts.measure


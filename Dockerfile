FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY . .
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd --create-home app && chown -R app:app /app
USER app
EXPOSE 8080
CMD ["uvicorn", "frontdesk_api.app:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]


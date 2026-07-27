FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache \
    PYTHONPATH="/app/src" \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-install-project

RUN adduser --system --group appuser \
    && mkdir -p /tmp/uv-cache \
    && chown -R appuser:appuser /tmp/uv-cache

COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser tests ./tests
COPY --chown=appuser:appuser alembic.ini ./alembic.ini
COPY --chown=appuser:appuser migrations ./migrations

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "delivery_service.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]



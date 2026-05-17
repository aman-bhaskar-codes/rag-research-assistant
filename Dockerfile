# ── Stage 1: Dependency Builder ─────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

RUN pip install uv --no-cache-dir

COPY backend/requirements.txt ./requirements.txt

RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r requirements.txt --no-cache

# ── Stage 2: Production Image ────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /venv /venv
COPY backend/ ./backend/

ENV PYTHONPATH=/app
ENV PATH="/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

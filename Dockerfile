# ── Stage 1: dependency resolver ─────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install uv (fast dependency installer)
RUN pip install uv --no-cache-dir

# Copy requirements file
COPY backend/requirements.txt ./requirements.txt

# Create venv and install dependencies
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r requirements.txt --no-cache

# ── Stage 2: production image ────────────────────────────────────
FROM python:3.11-slim

# System libs needed for psycopg2 & sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv from builder — no pip install in prod image
COPY --from=builder /venv /venv

# Copy application source
COPY backend/ ./backend/

# PYTHONPATH points at /app so imports are "backend.app.x"
ENV PYTHONPATH=/app
ENV PATH="/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

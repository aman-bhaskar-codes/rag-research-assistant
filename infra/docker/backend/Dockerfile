# ──────────────────────────────────────────────────────────────────────────────
# RAG Research Assistant — Backend (Cloud Run Optimized)
# ──────────────────────────────────────────────────────────────────────────────

# 1. Base image — slim for fast cold starts, 3.11 for production stability
FROM python:3.11-slim

# 2. Prevent .pyc files and ensure real-time log output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies
#    - build-essential: needed for compiling native extensions (numpy, scikit-learn)
#    - libpq-dev: required by asyncpg for PostgreSQL connections
#    - curl: health check probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy dependency file FIRST (Docker layer caching)
COPY backend/requirements.txt .

# 6. Install Python dependencies (no cache = smaller image)
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir python-multipart

# 7. Create non-root user (Cloud Run security best practice)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# 8. Copy backend application code
COPY backend/ .

# 9. Switch to non-root user
USER appuser

# 10. Expose port (Cloud Run injects PORT env var, default 8080)
EXPOSE 8080

# 11. Health check (Cloud Run uses HTTP probes, but this helps local testing)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# 12. Start server — respects Cloud Run's PORT injection
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

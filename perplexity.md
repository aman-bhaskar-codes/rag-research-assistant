# PERPLEXITY CLONE — MASTER AGENT EXECUTION PLAN

### `rag-research-assistant` → Full Perplexity Clone with Ollama

> **FOR OPUS AGENT:** Read every section before running any command. Each step has a `✅ VERIFY` block — run it before moving to the next step. If any verify fails, debug it inline before continuing. Do NOT skip phases. Execute every code block exactly as written.

---

## 🧭 REPO AUDIT (State Before We Start)

| File | Status | Problem |
|------|--------|---------|
| `Dockerfile` | ❌ BROKEN | Copies `backend/requirements.txt` (doesn't exist), wrong PYTHONPATH |
| `pyproject.toml` | ❌ INCOMPLETE | Missing `fastapi`, `uvicorn`, `ollama`, `pydantic-settings`, `httpx` |
| `docker-compose.yml` | ❌ BROKEN | `version: '3.8'` deprecated, `ankane/pgvector` deprecated, no healthchecks |
| `.env.neon` | 🔴 CRITICAL | Live credentials committed to public repo — must be purged |
| `.DS_Store` | ⚠️ JUNK | macOS artifact committed, should be removed |
| `main.py` (root) | ❌ STUB | Prints "Hello" — no application |
| `backend/` | ⚠️ PARTIAL | Architecture described, implementation missing |
| `frontend/` | ⚠️ PARTIAL | Exists but not Perplexity-grade |
| `.gitignore` | ⚠️ WEAK | Doesn't exclude `.env.*` files |

**MODELS AVAILABLE (Ollama, already pulled):**

- `llama3.2:3b` — fast, general reasoning (default)
- `phi4-mini:latest` — Microsoft, strong at math/code
- `qwen2.5:3b` — multilingual, strong at structured data

**FREE SERVICES WE USE:**

- Neon (Serverless Postgres + pgvector) — free tier
- Upstash (HTTP Redis) — free 10k req/day
- Brave Search API — free 2000 queries/month
- Tavily API — free 1000 queries/month (fallback)
- Vercel — free Next.js hosting
- Google Cloud Run — free 2M requests/month
- Ollama — fully local, $0 always

---

## 🏗️ TARGET ARCHITECTURE — PERPLEXITY CLONE

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                        │
│  ┌──────────┐  ┌─────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Search   │  │  Answer +   │  │ Sources  │  │ History +      │  │
│  │ Bar      │  │  Citations  │  │ Panel    │  │ Settings       │  │
│  │ + Focus  │  │  Streaming  │  │ [1][2]   │  │ Model Picker   │  │
│  └──────────┘  └─────────────┘  └──────────┘  └────────────────┘  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ SSE Stream
┌──────────────────────────▼──────────────────────────────────────────┐
│                   API GATEWAY (FastAPI + Uvicorn)                    │
│  /search/stream    /documents/ingest    /models    /history         │
└──────┬──────────────────────┬───────────────────────┬───────────────┘
       │                      │                       │
┌──────▼──────┐   ┌───────────▼──────────┐  ┌────────▼──────────────┐
│  QUERY      │   │   RAG ENGINE         │  │   MEMORY LAYER        │
│  PIPELINE   │   │                      │  │                        │
│  ├─ Classify│   │  ├─ PDF Ingestion    │  │  ├─ Redis (short-term) │
│  ├─ Rewrite │   │  ├─ Chunking         │  │  ├─ Postgres (long)    │
│  ├─ Expand  │   │  ├─ Embeddings       │  │  └─ Search History     │
│  └─ Route   │   │  ├─ pgvector search  │  │                        │
│             │   │  ├─ BM25 search      │  └────────────────────────┘
│  WEB SEARCH │   │  ├─ RRF Fusion       │
│  ├─ Brave   │   │  └─ Cross-Encoder    │
│  └─ Tavily  │   │     Reranker         │
└──────┬──────┘   └───────────┬──────────┘
       │                      │
┌──────▼──────────────────────▼──────────────────────────────────────┐
│                      LLM ROUTER                                      │
│  llama3.2:3b (default)  │  phi4-mini (code/math)  │  qwen2.5 (multi)│
│                      Ollama Local                                    │
└──────────────────────────────────────────────────────────────────────┘
```

**Perplexity UX Features We Clone:**

1. Centered search bar homepage with focus mode pills
2. Split-pane answer: left = streaming markdown + citations, right = sources
3. Numbered inline citations `[1]` `[2]` linking to sources
4. "Related Questions" auto-generated below every answer
5. Left sidebar: search history, collections, settings
6. Model selector dropdown in header
7. Focus modes: General, Academic, Code, Writing, Research
8. Dark mode default, light mode toggle
9. Copy answer, Share link, Thumbs up/down feedback
10. Follow-up question input under every answer

---

## PHASE 0 — EMERGENCY CLEANUP (Run First, Non-Negotiable)

### Step 0.1 — Rotate All Leaked Credentials

**AGENT: Do NOT write any code yet. Execute these credential rotations manually:**

1. **Neon PostgreSQL** → <https://console.neon.tech> → Settings → Reset password → copy new `DATABASE_URL`
2. **Upstash Redis** → <https://console.upstash.com> → your DB → REST API → Regenerate Token → copy new `REDIS_URL`
3. **Google Gemini** → <https://aistudio.google.com/apikey> → Delete old key → Create new → copy `GEMINI_API_KEY`
4. **Brave Search** → <https://brave.com/search/api/> → Sign up free → copy `BRAVE_API_KEY`
5. **Tavily** → <https://app.tavily.com> → Sign up free → copy `TAVILY_API_KEY`

Save all in a local `.env` file that is NEVER committed.

### Step 0.2 — Purge .env.neon from Git History

```bash
# In the repo root
pip install git-filter-repo

# Remove .env.neon from ALL commits in history
git filter-repo --path .env.neon --invert-paths --force

# Remove .DS_Store from ALL commits
git filter-repo --path .DS_Store --invert-paths --force

# Force push to overwrite GitHub history
git remote add origin https://github.com/aman-bhaskar-codes/rag-research-assistant.git
git push origin main --force
```

### Step 0.3 — Replace .gitignore

```bash
cat > .gitignore << 'EOF'
# Environment
.env
.env.*
!.env.example

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
.venv/
venv/
.uv/

# Node
node_modules/
.next/
out/
.vercel/

# macOS
.DS_Store
.AppleDouble
.LSOverride

# IDEs
.vscode/
.idea/
*.swp

# Docker
*.log

# Data
data/raw/
data/uploads/
*.pdf
!data/sample/

# Secrets
*.pem
*.key
secrets/
EOF
```

✅ **VERIFY:** `git status` shows `.env.neon` is untracked. Run `git log --oneline | head -5` and `git show HEAD:.env.neon` → should say "fatal: path not in this commit"

---

## PHASE 1 — PROJECT FOUNDATION

### Step 1.1 — New pyproject.toml

```bash
cat > pyproject.toml << 'EOF'
[project]
name = "rag-research-assistant"
version = "2.0.0"
description = "Perplexity-grade Research Assistant with Ollama + pgvector"
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    # ── Web Framework ─────────────────────────────────
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "python-multipart>=0.0.12",
    "sse-starlette>=2.1.0",

    # ── Database ──────────────────────────────────────
    "asyncpg>=0.31.0",
    "sqlalchemy[asyncio]>=2.0.48",
    "alembic>=1.14.0",
    "pgvector>=0.4.2",
    "psycopg2-binary>=2.9.11",

    # ── Cache ─────────────────────────────────────────
    "redis>=5.2.0",
    "upstash-redis>=1.1.0",

    # ── AI / Embeddings ───────────────────────────────
    "fastembed>=0.4.0",
    "sentence-transformers>=3.4.0",
    "rank-bm25>=0.2.2",
    "numpy>=1.26.0",
    "scikit-learn>=1.6.0",

    # ── LLM Clients ───────────────────────────────────
    "ollama>=0.4.4",
    "google-generativeai>=0.8.6",

    # ── Web Search ────────────────────────────────────
    "httpx>=0.28.1",
    "trafilatura>=2.0.0",
    "beautifulsoup4>=4.12.0",

    # ── Config & Utils ────────────────────────────────
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.2.2",
    "orjson>=3.10.0",
    "loguru>=0.7.3",
    "tenacity>=9.0.0",
    "pdfplumber>=0.11.4",
    "python-jose>=3.3.0",
    "passlib>=1.7.4",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.1",
    "black>=24.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = false
ignore_missing_imports = true
EOF
```

### Step 1.2 — Install with uv

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Sync all dependencies
uv sync
```

✅ **VERIFY:** `uv run python -c "import fastapi, uvicorn, ollama, fastembed; print('OK')"` → prints OK

### Step 1.3 — New Dockerfile (Multi-Stage)

```bash
cat > Dockerfile << 'EOF'
# ── Stage 1: Dependency Builder ─────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

RUN pip install uv --no-cache-dir

COPY pyproject.toml .
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -e . --no-cache

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

CMD ["uvicorn", "backend.app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--loop", "uvloop"]
EOF
```

### Step 1.4 — New docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
# Compose V2 — no version key needed

services:

  # ── PostgreSQL + pgvector ────────────────────────────────────────
  db:
    image: pgvector/pgvector:pg16-latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: perplexity_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d perplexity_db"]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 10s

  # ── Redis Cache ──────────────────────────────────────────────────
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru --save ""
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # ── FastAPI Backend ──────────────────────────────────────────────
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/perplexity_db
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    develop:
      watch:
        - action: sync
          path: ./backend
          target: /app/backend

  # ── Frontend (Next.js) ───────────────────────────────────────────
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - api

volumes:
  pgdata:
EOF
```

### Step 1.5 — .env.example (Unified)

```bash
cat > .env.example << 'EOF'
# ── App ──────────────────────────────────────────────────────────────
ENV=development
LOG_LEVEL=info
PORT=8000
SECRET_KEY=change-me-to-random-64-char-string

# ── Database (local docker-compose) ──────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/perplexity_db
# Production (Neon):
# DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/perplexity_db?sslmode=require

# ── Redis ─────────────────────────────────────────────────────────────
REDIS_URL=redis://cache:6379/0
# Production (Upstash):
# REDIS_URL=rediss://:token@us1-xxx.upstash.io:6380

# ── Ollama ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL=http://host.docker.internal:11434
DEFAULT_MODEL=llama3.2:3b
FAST_MODEL=llama3.2:3b
SMART_MODEL=phi4-mini:latest
MULTILINGUAL_MODEL=qwen2.5:3b

# ── Web Search ────────────────────────────────────────────────────────
BRAVE_API_KEY=your-brave-api-key
TAVILY_API_KEY=your-tavily-api-key
MAX_SEARCH_RESULTS=8

# ── Gemini (optional cloud fallback) ─────────────────────────────────
GEMINI_API_KEY=your-gemini-key

# ── RAG Tuning ────────────────────────────────────────────────────────
RAG_TOP_K=20
RAG_TOP_N=5
CHUNK_SIZE=400
CHUNK_OVERLAP=80
MAX_CONTEXT_MESSAGES=20
EMBED_MODEL=nomic-ai/nomic-embed-text-v1.5
EMBED_DIM=768
EOF

cp .env.example .env
```

✅ **VERIFY:** `cat .env` shows all keys. Fill in real values before continuing.

---

## PHASE 2 — BACKEND CORE

### Complete Directory Structure to Create

```bash
mkdir -p backend/app/routes
mkdir -p backend/rag_engine
mkdir -p backend/memory
mkdir -p backend/search
mkdir -p backend/utils
touch backend/__init__.py
touch backend/app/__init__.py
touch backend/app/routes/__init__.py
touch backend/rag_engine/__init__.py
touch backend/memory/__init__.py
touch backend/search/__init__.py
touch backend/utils/__init__.py
```

### Step 2.1 — Config (backend/app/config.py)

```bash
cat > backend/app/config.py << 'EOF'
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    env: str = "development"
    log_level: str = "info"
    port: int = 8000
    secret_key: str = "change-me"

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Ollama models
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:3b"
    fast_model: str = "llama3.2:3b"
    smart_model: str = "phi4-mini:latest"
    multilingual_model: str = "qwen2.5:3b"

    # Web Search
    brave_api_key: str | None = None
    tavily_api_key: str | None = None
    max_search_results: int = 8

    # Gemini fallback
    gemini_api_key: str | None = None

    # RAG
    rag_top_k: int = 20
    rag_top_n: int = 5
    chunk_size: int = 400
    chunk_overlap: int = 80
    max_context_messages: int = 20
    embed_model: str = "nomic-ai/nomic-embed-text-v1.5"
    embed_dim: int = 768

    @field_validator("database_url")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if "asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
EOF
```

### Step 2.2 — Database (backend/app/database.py)

```bash
cat > backend/app/database.py << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from loguru import logger
from backend.app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.env == "development",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        # Enable extensions
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        from backend.app import models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    logger.success("✅ Database ready with pgvector + pg_trgm")


async def close_db():
    await engine.dispose()


async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
EOF
```

### Step 2.3 — Models (backend/app/models.py)

```bash
cat > backend/app/models.py << 'EOF'
import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, DateTime, ForeignKey, Index,
    Integer, Boolean, Float, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from backend.app.database import Base
from backend.app.config import get_settings

settings = get_settings()
EMBED_DIM = settings.embed_dim


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(512))
    domain: Mapped[str] = mapped_column(String(64), index=True, default="general")
    source_type: Mapped[str] = mapped_column(String(32), default="upload")  # upload | web | paste
    source_url: Mapped[str | None] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    document: Mapped["Document"] = relationship(back_populates="chunks")

    __table_args__ = (
        Index(
            "ix_chunks_embedding_cosine",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"lists": "100"},
        ),
        Index(
            "ix_chunks_fts",
            "content",
            postgresql_using="gin",
            postgresql_ops={"content": "gin_trgm_ops"},
        ),
    )


class SearchSession(Base):
    __tablename__ = "search_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_key: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str | None] = mapped_column(String(256))
    focus_mode: Mapped[str] = mapped_column(String(32), default="general")
    model_used: Mapped[str] = mapped_column(String(64), default="llama3.2:3b")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    turns: Mapped[list["SearchTurn"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class SearchTurn(Base):
    __tablename__ = "search_turns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("search_sessions.id", ondelete="CASCADE"))
    query: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSON, default=list)
    related_questions: Mapped[list] = mapped_column(JSON, default=list)
    model_used: Mapped[str] = mapped_column(String(64))
    focus_mode: Mapped[str] = mapped_column(String(32))
    feedback: Mapped[int | None] = mapped_column(Integer)  # 1=up, -1=down
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    session: Mapped["SearchSession"] = relationship(back_populates="turns")


class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_key: Mapped[str] = mapped_column(String(128), index=True)
    summary: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    importance: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
EOF
```

### Step 2.4 — Main App Entry Point (backend/app/main.py)

```bash
cat > backend/app/main.py << 'EOF'
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
import sys

from backend.app.config import get_settings
from backend.app.database import init_db, close_db
from backend.memory.short_term import init_redis, close_redis
from backend.app.routes import search, documents, health, history, models, feedback

settings = get_settings()

# ── Logger Setup ──────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level=settings.log_level.upper(),
    colorize=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Perplexity Clone...")
    await init_db()
    await init_redis()
    logger.success("✅ All systems ready")
    yield
    logger.info("🛑 Shutting down...")
    await close_db()
    await close_redis()


app = FastAPI(
    title="Perplexity Clone API",
    description="Research Assistant with Ollama + pgvector + Web Search",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(search.router,    prefix="/search",    tags=["search"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(history.router,   prefix="/history",   tags=["history"])
app.include_router(models.router,    prefix="/models",    tags=["models"])
app.include_router(feedback.router,  prefix="/feedback",  tags=["feedback"])
EOF
```

### Step 2.5 — Health Route (backend/app/routes/health.py)

```bash
cat > backend/app/routes/health.py << 'EOF'
from fastapi import APIRouter
from sqlalchemy import text
from backend.app.database import engine
from backend.memory.short_term import get_redis

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    db_ok = redis_ok = ollama_ok = False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        pass

    try:
        r = await get_redis()
        await r.ping()
        redis_ok = True
    except Exception:
        pass

    try:
        import httpx
        from backend.app.config import get_settings
        s = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{s.ollama_base_url}/api/tags", timeout=3)
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    status = "ok" if (db_ok and redis_ok) else "degraded"
    return {
        "status": status,
        "db": db_ok,
        "redis": redis_ok,
        "ollama": ollama_ok,
        "version": "2.0.0",
    }
EOF
```

### Step 2.6 — Models Route (backend/app/routes/models.py)

```bash
cat > backend/app/routes/models.py << 'EOF'
from fastapi import APIRouter
import httpx
from backend.app.config import get_settings

router = APIRouter()
settings = get_settings()

AVAILABLE_MODELS = [
    {
        "id": "llama3.2:3b",
        "name": "Llama 3.2 (3B)",
        "description": "Fast, general-purpose. Best for most queries.",
        "size": "2.0 GB",
        "strengths": ["general", "fast", "reasoning"],
        "is_default": True,
    },
    {
        "id": "phi4-mini:latest",
        "name": "Phi-4 Mini",
        "description": "Microsoft. Excellent at code and math.",
        "size": "2.5 GB",
        "strengths": ["code", "math", "structured"],
        "is_default": False,
    },
    {
        "id": "qwen2.5:3b",
        "name": "Qwen 2.5 (3B)",
        "description": "Alibaba. Multilingual, strong structured output.",
        "size": "1.9 GB",
        "strengths": ["multilingual", "data", "structured"],
        "is_default": False,
    },
]


@router.get("")
async def list_models():
    """List available Ollama models with their status."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
            pulled = {m["name"] for m in resp.json().get("models", [])}
    except Exception:
        pulled = set()

    for m in AVAILABLE_MODELS:
        m["available"] = m["id"] in pulled or any(
            m["id"].split(":")[0] in p for p in pulled
        )

    return {"models": AVAILABLE_MODELS}


@router.get("/recommend")
async def recommend_model(focus: str = "general", query: str = ""):
    """Recommend the best model for a given focus mode."""
    mapping = {
        "code": "phi4-mini:latest",
        "math": "phi4-mini:latest",
        "academic": "phi4-mini:latest",
        "multilingual": "qwen2.5:3b",
        "research": "llama3.2:3b",
        "general": "llama3.2:3b",
        "writing": "llama3.2:3b",
    }
    return {"recommended": mapping.get(focus, settings.default_model)}
EOF
```

### Step 2.7 — Feedback Route (backend/app/routes/feedback.py)

```bash
cat > backend/app/routes/feedback.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_session
from backend.app.models import SearchTurn
import uuid

router = APIRouter()


class FeedbackRequest(BaseModel):
    turn_id: str
    feedback: int  # 1 = thumbs up, -1 = thumbs down


@router.post("")
async def submit_feedback(
    req: FeedbackRequest,
    session: AsyncSession = Depends(get_session),
):
    turn = await session.get(SearchTurn, uuid.UUID(req.turn_id))
    if not turn:
        raise HTTPException(404, "Turn not found")
    turn.feedback = req.feedback
    await session.commit()
    return {"ok": True}
EOF
```

### Step 2.8 — History Route (backend/app/routes/history.py)

```bash
cat > backend/app/routes/history.py << 'EOF'
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.database import get_session
from backend.app.models import SearchSession, SearchTurn

router = APIRouter()


@router.get("")
async def get_history(
    session_key: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(SearchSession)
        .where(SearchSession.session_key == session_key)
        .order_by(desc(SearchSession.updated_at))
        .limit(limit)
        .options(selectinload(SearchSession.turns))
    )
    sessions = result.scalars().all()

    return {
        "sessions": [
            {
                "id": str(s.id),
                "title": s.title,
                "focus_mode": s.focus_mode,
                "model_used": s.model_used,
                "created_at": s.created_at.isoformat(),
                "turn_count": len(s.turns),
                "last_query": s.turns[-1].query if s.turns else None,
            }
            for s in sessions
        ]
    }


@router.get("/{session_id}")
async def get_session_detail(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy.orm import selectinload
    import uuid
    result = await session.get(
        SearchSession, uuid.UUID(session_id),
        options=[selectinload(SearchSession.turns)]
    )
    if not result:
        from fastapi import HTTPException
        raise HTTPException(404, "Session not found")

    return {
        "id": str(result.id),
        "title": result.title,
        "focus_mode": result.focus_mode,
        "model_used": result.model_used,
        "turns": [
            {
                "id": str(t.id),
                "query": t.query,
                "answer": t.answer,
                "sources": t.sources,
                "related_questions": t.related_questions,
                "model_used": t.model_used,
                "created_at": t.created_at.isoformat(),
                "feedback": t.feedback,
            }
            for t in result.turns
        ],
    }
EOF
```

---

## PHASE 3 — MEMORY LAYER

### Step 3.1 — Redis Short-Term Memory (backend/memory/short_term.py)

```bash
cat > backend/memory/short_term.py << 'EOF'
import json
from typing import AsyncGenerator
import redis.asyncio as aioredis
from backend.app.config import get_settings

settings = get_settings()
_redis: aioredis.Redis | None = None


async def init_redis():
    global _redis
    _redis = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=20,
    )
    await _redis.ping()


async def close_redis():
    if _redis:
        await _redis.aclose()


async def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialised")
    return _redis


def _key(session_id: str) -> str:
    return f"chat:{session_id}:messages"


async def push_message(session_id: str, role: str, content: str) -> None:
    r = await get_redis()
    msg = json.dumps({"role": role, "content": content})
    key = _key(session_id)
    await r.rpush(key, msg)
    await r.ltrim(key, -settings.max_context_messages, -1)
    await r.expire(key, 86400)  # 24h TTL


async def get_history(session_id: str) -> list[dict]:
    r = await get_redis()
    msgs = await r.lrange(_key(session_id), 0, -1)
    return [json.loads(m) for m in msgs]


async def clear_history(session_id: str) -> None:
    r = await get_redis()
    await r.delete(_key(session_id))


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    r = await get_redis()
    await r.setex(f"cache:{key}", ttl, value)


async def cache_get(key: str) -> str | None:
    r = await get_redis()
    return await r.get(f"cache:{key}")
EOF
```

---

## PHASE 4 — WEB SEARCH ENGINE

### Step 4.1 — Brave Search Client (backend/search/brave.py)

```bash
cat > backend/search/brave.py << 'EOF'
"""Brave Search API — free tier: 2000 queries/month."""
import httpx
from loguru import logger
from backend.app.config import get_settings

settings = get_settings()

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


async def brave_search(query: str, count: int = 8) -> list[dict]:
    if not settings.brave_api_key:
        logger.warning("BRAVE_API_KEY not set, skipping Brave search")
        return []

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": settings.brave_api_key,
    }
    params = {
        "q": query,
        "count": min(count, 20),
        "search_lang": "en",
        "safesearch": "moderate",
        "freshness": "pw",  # past week
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(BRAVE_SEARCH_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("web", {}).get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("description", ""),
            "source": "brave",
        })
    return results
EOF
```

### Step 4.2 — Tavily Search Client (backend/search/tavily.py)

```bash
cat > backend/search/tavily.py << 'EOF'
"""Tavily Search API — free tier: 1000 queries/month. Fallback when Brave fails."""
import httpx
from loguru import logger
from backend.app.config import get_settings

settings = get_settings()

TAVILY_URL = "https://api.tavily.com/search"


async def tavily_search(query: str, count: int = 8) -> list[dict]:
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not set, skipping Tavily search")
        return []

    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
        "max_results": min(count, 10),
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(TAVILY_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("content", "")[:300],
            "source": "tavily",
        })
    return results
EOF
```

### Step 4.3 — Content Fetcher (backend/search/fetcher.py)

```bash
cat > backend/search/fetcher.py << 'EOF'
"""Fetch and extract clean text content from web URLs."""
import asyncio
import httpx
import trafilatura
from loguru import logger


async def fetch_and_extract(url: str, timeout: int = 8) -> str | None:
    """Download a URL and extract its main text content."""
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Research Bot)"},
        ) as client:
            resp = await client.get(url, timeout=timeout)
            if resp.status_code != 200:
                return None
            html = resp.text

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )
        return text[:3000] if text else None  # Cap at 3000 chars per source

    except Exception as e:
        logger.debug(f"Failed to fetch {url}: {e}")
        return None


async def fetch_sources_parallel(urls: list[str], max_concurrent: int = 4) -> dict[str, str]:
    """Fetch multiple URLs concurrently. Returns {url: content} dict."""
    sem = asyncio.Semaphore(max_concurrent)

    async def fetch_one(url: str) -> tuple[str, str | None]:
        async with sem:
            content = await fetch_and_extract(url)
            return url, content

    tasks = [fetch_one(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        url: content
        for url, content in results
        if isinstance(content, str) and content
    }
EOF
```

### Step 4.4 — Search Router (backend/search/router.py)

```bash
cat > backend/search/router.py << 'EOF'
"""Routes queries to Brave, Tavily, or RAG based on focus mode."""
import asyncio
from loguru import logger
from backend.search.brave import brave_search
from backend.search.tavily import tavily_search
from backend.search.fetcher import fetch_sources_parallel
from backend.app.config import get_settings

settings = get_settings()

FOCUS_TO_SEARCH_STRATEGY = {
    "general":      "web",
    "academic":     "web",
    "code":         "web",
    "writing":      "rag",   # Only local docs
    "research":     "both",  # Web + RAG
    "documents":    "rag",
}


async def run_web_search(query: str, count: int = 8) -> list[dict]:
    """Try Brave first, fall back to Tavily."""
    sources = []

    try:
        sources = await brave_search(query, count)
        logger.debug(f"Brave returned {len(sources)} results")
    except Exception as e:
        logger.warning(f"Brave failed: {e}")

    if not sources:
        try:
            sources = await tavily_search(query, count)
            logger.debug(f"Tavily returned {len(sources)} results")
        except Exception as e:
            logger.warning(f"Tavily failed: {e}")

    return sources[:count]


async def enrich_sources(sources: list[dict]) -> list[dict]:
    """Fetch full content from each source URL in parallel."""
    if not sources:
        return sources

    urls = [s["url"] for s in sources if s.get("url")]
    contents = await fetch_sources_parallel(urls, max_concurrent=4)

    for source in sources:
        url = source.get("url", "")
        source["content"] = contents.get(url, source.get("description", ""))
        source["content_length"] = len(source["content"])

    return sources
EOF
```

---

## PHASE 5 — RAG ENGINE

### Step 5.1 — Embeddings (backend/rag_engine/embeddings.py)

```bash
cat > backend/rag_engine/embeddings.py << 'EOF'
from functools import lru_cache
from fastembed import TextEmbedding
from backend.app.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def _get_model() -> TextEmbedding:
    return TextEmbedding(settings.embed_model, max_length=512)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return [v.tolist() for v in model.embed(texts)]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
EOF
```

### Step 5.2 — Chunker (backend/rag_engine/chunker.py)

```bash
cat > backend/rag_engine/chunker.py << 'EOF'
"""
Domain-aware recursive text chunker.
- Code: splits at function/class boundaries
- Academic: splits at paragraph boundaries
- General: splits at sentence boundaries with overlap
"""
import re
from dataclasses import dataclass
from backend.app.config import get_settings

settings = get_settings()


@dataclass
class TextChunk:
    content: str
    index: int
    meta: dict


def _split_sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def _split_code_blocks(text: str) -> list[str]:
    """Split code at function/class definitions."""
    pattern = r"(?=(?:def |class |async def |function |const |export ))"
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    domain: str = "general",
    size: int | None = None,
    overlap: int | None = None,
) -> list[TextChunk]:
    size = size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    # Clean common noise
    text = re.sub(r"\[[\d,\s]+\]", "", text)   # Remove [1], [2,3]
    text = re.sub(r"\s{3,}", "\n", text)         # Collapse whitespace
    text = text.strip()

    # Domain-specific splitting
    if domain == "code":
        units = _split_code_blocks(text)
    elif domain == "academic":
        units = _split_paragraphs(text)
    else:
        units = _split_sentences(text)

    # Build chunks with overlap
    chunks: list[TextChunk] = []
    current_words: list[str] = []
    idx = 0

    for unit in units:
        unit_words = unit.split()
        if len(current_words) + len(unit_words) > size and current_words:
            content = " ".join(current_words)
            chunks.append(TextChunk(
                content=content,
                index=idx,
                meta={"domain": domain, "word_count": len(current_words)},
            ))
            # Keep overlap
            current_words = current_words[-overlap:]
            idx += 1

        current_words.extend(unit_words)

    if current_words:
        chunks.append(TextChunk(
            content=" ".join(current_words),
            index=idx,
            meta={"domain": domain, "word_count": len(current_words)},
        ))

    return chunks
EOF
```

### Step 5.3 — Ingestion (backend/rag_engine/ingestion.py)

```bash
cat > backend/rag_engine/ingestion.py << 'EOF'
import pdfplumber
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models import Document, Chunk
from backend.rag_engine.embeddings import embed_texts
from backend.rag_engine.chunker import chunk_text


def extract_pdf_text(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages)


async def ingest_document(
    text: str,
    filename: str,
    domain: str,
    source_type: str = "upload",
    source_url: str | None = None,
    session: AsyncSession = None,
) -> dict:
    chunks = chunk_text(text, domain=domain)

    doc = Document(
        filename=filename,
        domain=domain,
        source_type=source_type,
        source_url=source_url,
        word_count=len(text.split()),
    )
    session.add(doc)
    await session.flush()

    texts = [c.content for c in chunks]
    vectors = embed_texts(texts)

    for chunk, vec in zip(chunks, vectors):
        session.add(Chunk(
            document_id=doc.id,
            content=chunk.content,
            embedding=vec,
            chunk_index=chunk.index,
            meta={**chunk.meta, "filename": filename},
        ))

    await session.commit()
    logger.success(f"Ingested '{filename}' → {len(chunks)} chunks in domain '{domain}'")
    return {"document_id": str(doc.id), "chunks": len(chunks), "domain": domain}
EOF
```

### Step 5.4 — Retriever (backend/rag_engine/retriever.py)

```bash
cat > backend/rag_engine/retriever.py << 'EOF'
from dataclasses import dataclass, field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()
RRF_K = 60  # Reciprocal Rank Fusion constant (from original paper)


@dataclass
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    meta: dict = field(default_factory=dict)
    source: str = "rag"


async def vector_search(
    vector: list[float],
    session: AsyncSession,
    top_k: int = 20,
    domain: str | None = None,
) -> list[tuple[str, str, dict, float]]:
    domain_filter = "AND meta->>'domain' = :domain" if domain else ""
    rows = await session.execute(text(f"""
        SELECT id::text, content, meta,
               1 - (embedding <=> :vec::vector) AS score
        FROM chunks
        WHERE 1=1 {domain_filter}
        ORDER BY embedding <=> :vec::vector
        LIMIT :k
    """), {"vec": str(vector), "k": top_k, **({"domain": domain} if domain else {})})
    return rows.fetchall()


async def bm25_search(
    query: str,
    session: AsyncSession,
    top_k: int = 20,
    domain: str | None = None,
) -> list[tuple[str, str, dict, float]]:
    domain_filter = "AND meta->>'domain' = :domain" if domain else ""
    rows = await session.execute(text(f"""
        SELECT id::text, content, meta,
               ts_rank(to_tsvector('english', content),
                       plainto_tsquery('english', :q)) AS score
        FROM chunks
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :q)
        {domain_filter}
        ORDER BY score DESC
        LIMIT :k
    """), {"q": query, "k": top_k, **({"domain": domain} if domain else {})})
    return rows.fetchall()


async def retrieve(
    query: str,
    session: AsyncSession,
    top_k: int | None = None,
    domain: str | None = None,
) -> list[RetrievedChunk]:
    top_k = top_k or settings.rag_top_k

    # Embed query
    vector = embed_query(query)

    # Run both retrievers in parallel
    import asyncio
    vector_rows, bm25_rows = await asyncio.gather(
        vector_search(vector, session, top_k, domain),
        bm25_search(query, session, top_k, domain),
    )

    # RRF Fusion
    scores: dict[str, float] = {}
    data: dict[str, tuple[str, dict]] = {}

    for rank, row in enumerate(vector_rows):
        scores[row[0]] = scores.get(row[0], 0) + 1 / (RRF_K + rank + 1)
        data[row[0]] = (row[1], row[2] or {})

    for rank, row in enumerate(bm25_rows):
        scores[row[0]] = scores.get(row[0], 0) + 1 / (RRF_K + rank + 1)
        data[row[0]] = (row[1], row[2] or {})

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [
        RetrievedChunk(
            chunk_id=cid,
            content=data[cid][0],
            score=score,
            meta=data[cid][1],
        )
        for cid, score in ranked[:top_k]
    ]
EOF
```

### Step 5.5 — Reranker (backend/rag_engine/reranker.py)

```bash
cat > backend/rag_engine/reranker.py << 'EOF'
from functools import lru_cache
from sentence_transformers import CrossEncoder
from backend.rag_engine.retriever import RetrievedChunk
from backend.app.config import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    top_n: int | None = None,
) -> list[RetrievedChunk]:
    top_n = top_n or settings.rag_top_n
    if not chunks:
        return []

    reranker = _get_reranker()
    pairs = [(query, c.content) for c in chunks]
    scores = reranker.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk.score = float(score)

    return sorted(chunks, key=lambda c: c.score, reverse=True)[:top_n]
EOF
```

### Step 5.6 — HyDE (backend/rag_engine/hyde.py)

```bash
cat > backend/rag_engine/hyde.py << 'EOF'
import ollama
from backend.app.config import get_settings

settings = get_settings()

HYDE_PROMPT = """Write a short, precise, factual paragraph that directly answers this question.
Be technical. Be specific. Do not hedge.

Question: {query}

Answer:"""


async def generate_hyde_doc(query: str) -> str:
    """Generate a hypothetical answer to embed instead of the raw query.
    This dramatically improves recall for abstract or high-level questions."""
    try:
        client = ollama.AsyncClient(host=settings.ollama_base_url)
        response = await client.generate(
            model=settings.fast_model,
            prompt=HYDE_PROMPT.format(query=query),
            options={"temperature": 0.1, "num_predict": 200},
        )
        return response["response"]
    except Exception:
        return query  # fallback to original query
EOF
```

---

## PHASE 6 — LLM LAYER

### Step 6.1 — LLM Router (backend/utils/llm_router.py)

```bash
cat > backend/utils/llm_router.py << 'EOF'
"""Routes queries to the right Ollama model based on focus mode and content."""
from backend.app.config import get_settings

settings = get_settings()


def select_model(focus_mode: str, requested_model: str | None = None) -> str:
    """Choose the best model for this focus mode.
    User-requested model always wins if specified.
    """
    if requested_model:
        return requested_model

    routing = {
        "code":          settings.smart_model,    # phi4-mini
        "math":          settings.smart_model,    # phi4-mini
        "academic":      settings.smart_model,    # phi4-mini
        "multilingual":  settings.multilingual_model,  # qwen2.5
        "general":       settings.fast_model,     # llama3.2
        "writing":       settings.fast_model,     # llama3.2
        "research":      settings.fast_model,     # llama3.2
        "documents":     settings.fast_model,     # llama3.2
    }
    return routing.get(focus_mode, settings.default_model)
EOF
```

### Step 6.2 — Prompt Builder (backend/utils/prompts.py)

```bash
cat > backend/utils/prompts.py << 'EOF'
"""Perplexity-style prompts that produce cited, structured answers."""

SYSTEM_PROMPT = """You are a research assistant like Perplexity AI.

You have been given search results and/or document excerpts as context.

RULES:
1. Answer factually using ONLY the provided context.
2. Cite sources inline using [1], [2], [3] notation — one per sentence or claim.
3. If the context doesn't contain the answer, say so clearly.
4. Format your answer in clean Markdown.
5. Keep answers concise but complete. No filler phrases.
6. Never fabricate facts or citations.

CONTEXT:
{context}

CITATION GUIDE:
{citation_guide}
"""

RELATED_QUESTIONS_PROMPT = """Based on this research query and answer, generate exactly 4 follow-up questions a curious researcher would ask next.

Query: {query}
Answer summary: {answer_summary}

Output ONLY a JSON array of 4 strings. No markdown, no explanation:
["question 1", "question 2", "question 3", "question 4"]"""


def build_context_and_citations(sources: list[dict], rag_chunks: list) -> tuple[str, str, list[dict]]:
    """
    Merge web sources + RAG chunks into context string with citation numbers.
    Returns: (context_text, citation_guide, numbered_sources_list)
    """
    numbered: list[dict] = []
    context_parts: list[str] = []
    citation_lines: list[str] = []

    for i, src in enumerate(sources, 1):
        content = src.get("content") or src.get("description", "")
        if not content:
            continue
        numbered.append({
            "index": i,
            "title": src.get("title", f"Source {i}"),
            "url": src.get("url", ""),
            "description": src.get("description", ""),
            "type": "web",
        })
        context_parts.append(f"[{i}] {content[:800]}")
        citation_lines.append(f"[{i}] {src.get('title', 'Web')} — {src.get('url', '')}")

    offset = len(numbered)
    for j, chunk in enumerate(rag_chunks, offset + 1):
        numbered.append({
            "index": j,
            "title": chunk.meta.get("filename", "Document"),
            "url": "",
            "description": chunk.content[:150],
            "type": "document",
        })
        context_parts.append(f"[{j}] {chunk.content[:800]}")
        citation_lines.append(f"[{j}] {chunk.meta.get('filename', 'Document')}")

    context = "\n\n".join(context_parts)
    citation_guide = "\n".join(citation_lines)

    return context, citation_guide, numbered
EOF
```

---

## PHASE 7 — SEARCH API ROUTE (The Core Engine)

### Step 7.1 — Main Search Route (backend/app/routes/search.py)

```bash
cat > backend/app/routes/search.py << 'EOF'
"""
Core Perplexity-style search endpoint.
Streams: sources → answer tokens → related questions → done
"""
import json
import uuid
import asyncio
from typing import AsyncGenerator

import ollama
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.app.config import get_settings
from backend.app.database import get_session
from backend.app.models import SearchSession, SearchTurn
from backend.memory.short_term import push_message, get_history
from backend.search.router import run_web_search, enrich_sources
from backend.rag_engine.retriever import retrieve
from backend.rag_engine.reranker import rerank
from backend.rag_engine.hyde import generate_hyde_doc
from backend.utils.llm_router import select_model
from backend.utils.prompts import (
    SYSTEM_PROMPT, RELATED_QUESTIONS_PROMPT, build_context_and_citations
)

router = APIRouter()
settings = get_settings()

FOCUS_MODES = {"general", "academic", "code", "writing", "research", "documents"}


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    focus_mode: str = Field(default="general")
    model: str | None = None
    use_web: bool = True
    use_rag: bool = True
    use_hyde: bool = False  # Disabled by default for speed; enable for academic mode


async def _stream_perplexity(
    query: str,
    session_id: str,
    focus_mode: str,
    model: str,
    use_web: bool,
    use_rag: bool,
    use_hyde: bool,
    db_session: AsyncSession,
) -> AsyncGenerator[str, None]:
    """
    SSE stream protocol:
    - event: sources     → JSON array of source objects
    - event: token       → one LLM token string
    - event: related     → JSON array of 4 follow-up questions
    - event: done        → final metadata JSON
    - event: error       → error message string
    """

    def sse(event: str, data) -> str:
        payload = data if isinstance(data, str) else json.dumps(data)
        return f"event: {event}\ndata: {payload}\n\n"

    sources: list[dict] = []
    rag_chunks = []
    full_answer = ""

    try:
        # ── STEP 1: Gather Sources ──────────────────────────────────────────
        tasks = []
        if use_web:
            tasks.append(run_web_search(query, count=settings.max_search_results))
        if use_rag:
            # HyDE for academic/research modes
            rag_query = query
            if use_hyde or focus_mode in ("academic", "research"):
                rag_query = await generate_hyde_doc(query)
            tasks.append(retrieve(rag_query, db_session, domain=focus_mode if focus_mode == "documents" else None))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        web_results = results[0] if use_web and not isinstance(results[0], Exception) else []
        rag_results = results[1 if use_web else 0] if use_rag and len(results) > (1 if use_web else 0) else []
        if isinstance(rag_results, Exception):
            rag_results = []

        # Enrich web sources with full content
        if web_results:
            sources = await enrich_sources(web_results)

        # Rerank RAG results
        if rag_results:
            rag_chunks = rerank(query, list(rag_results), top_n=settings.rag_top_n)

        # ── STEP 2: Emit Sources Immediately ───────────────────────────────
        yield sse("sources", [
            {
                "index": i + 1,
                "title": s.get("title", ""),
                "url": s.get("url", ""),
                "description": s.get("description", "")[:200],
                "type": "web",
            }
            for i, s in enumerate(sources)
        ] + [
            {
                "index": len(sources) + i + 1,
                "title": c.meta.get("filename", "Document"),
                "url": "",
                "description": c.content[:150],
                "type": "document",
            }
            for i, c in enumerate(rag_chunks)
        ])

        # ── STEP 3: Build Prompt ────────────────────────────────────────────
        context, citation_guide, numbered_sources = build_context_and_citations(sources, rag_chunks)

        if not context.strip():
            yield sse("error", "No sources found for this query. Try a different search.")
            return

        chat_history = await get_history(session_id)

        messages = [{"role": "system", "content": SYSTEM_PROMPT.format(
            context=context,
            citation_guide=citation_guide,
        )}]
        messages += chat_history[-6:]  # Last 3 exchanges
        messages.append({"role": "user", "content": query})

        # ── STEP 4: Stream LLM Answer ───────────────────────────────────────
        client = ollama.AsyncClient(host=settings.ollama_base_url)

        async for chunk in await client.chat(
            model=model,
            messages=messages,
            stream=True,
            options={"temperature": 0.3, "num_ctx": 4096},
        ):
            token = chunk["message"]["content"]
            full_answer += token
            yield sse("token", token)

        # ── STEP 5: Generate Related Questions ─────────────────────────────
        related_questions = []
        try:
            related_prompt = RELATED_QUESTIONS_PROMPT.format(
                query=query,
                answer_summary=full_answer[:500],
            )
            related_resp = await client.generate(
                model=settings.fast_model,
                prompt=related_prompt,
                options={"temperature": 0.7, "num_predict": 200},
            )
            raw = related_resp["response"].strip()
            # Parse JSON array
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start != -1 and end > start:
                related_questions = json.loads(raw[start:end])
        except Exception as e:
            logger.debug(f"Related questions generation failed: {e}")

        yield sse("related", related_questions)

        # ── STEP 6: Persist to Database ─────────────────────────────────────
        try:
            # Upsert session
            from sqlalchemy import select
            stmt = select(SearchSession).where(
                SearchSession.session_key == session_id
            )
            result = await db_session.execute(stmt)
            sess = result.scalar_one_or_none()

            if not sess:
                sess = SearchSession(
                    session_key=session_id,
                    title=query[:80],
                    focus_mode=focus_mode,
                    model_used=model,
                )
                db_session.add(sess)
                await db_session.flush()

            turn = SearchTurn(
                session_id=sess.id,
                query=query,
                answer=full_answer,
                sources=numbered_sources,
                related_questions=related_questions,
                model_used=model,
                focus_mode=focus_mode,
            )
            db_session.add(turn)
            await db_session.commit()

            # Short-term memory
            await push_message(session_id, "user", query)
            await push_message(session_id, "assistant", full_answer[:500])

            yield sse("done", {
                "turn_id": str(turn.id),
                "session_id": session_id,
                "model": model,
                "sources_count": len(numbered_sources),
            })

        except Exception as e:
            logger.error(f"DB persist failed: {e}")
            yield sse("done", {"session_id": session_id, "error": str(e)})

    except Exception as e:
        logger.error(f"Search pipeline error: {e}", exc_info=True)
        yield sse("error", f"Search failed: {str(e)}")


@router.post("/stream")
async def search_stream(
    req: SearchRequest,
    db_session: AsyncSession = Depends(get_session),
):
    if req.focus_mode not in FOCUS_MODES:
        raise HTTPException(400, f"Invalid focus_mode. Must be one of: {FOCUS_MODES}")

    model = select_model(req.focus_mode, req.model)

    return StreamingResponse(
        _stream_perplexity(
            query=req.query,
            session_id=req.session_id,
            focus_mode=req.focus_mode,
            model=model,
            use_web=req.use_web,
            use_rag=req.use_rag,
            use_hyde=req.use_hyde,
            db_session=db_session,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/suggest")
async def suggest_queries(q: str):
    """Auto-complete query suggestions powered by local LLM."""
    from backend.app.config import get_settings
    s = get_settings()
    client = ollama.AsyncClient(host=s.ollama_base_url)
    prompt = f"""Generate 5 search query auto-completions for: "{q}"
Output ONLY a JSON array of 5 strings."""
    try:
        resp = await client.generate(
            model=s.fast_model,
            prompt=prompt,
            options={"temperature": 0.5, "num_predict": 100},
        )
        raw = resp["response"].strip()
        start, end = raw.find("["), raw.rfind("]") + 1
        suggestions = json.loads(raw[start:end]) if start != -1 else []
    except Exception:
        suggestions = []
    return {"suggestions": suggestions[:5]}
EOF
```

### Step 7.2 — Documents Route (backend/app/routes/documents.py)

```bash
cat > backend/app/routes/documents.py << 'EOF'
import tempfile
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_session
from backend.rag_engine.ingestion import ingest_document, extract_pdf_text

router = APIRouter()

ALLOWED_TYPES = {"application/pdf", "text/plain", "text/markdown"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("/ingest")
async def ingest_document_route(
    file: UploadFile = File(...),
    domain: str = Form(default="general"),
    session: AsyncSession = Depends(get_session),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, f"Unsupported file type: {file.content_type}. Use PDF or text.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large. Max 20MB.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if file.content_type == "application/pdf":
            text = extract_pdf_text(tmp_path)
        else:
            text = content.decode("utf-8", errors="ignore")

        if len(text.split()) < 20:
            raise HTTPException(422, "Document appears empty or unreadable.")

        result = await ingest_document(
            text=text,
            filename=file.filename,
            domain=domain,
            source_type="upload",
            session=session,
        )
        return result
    finally:
        os.unlink(tmp_path)


@router.post("/ingest-text")
async def ingest_text(
    text: str = Form(...),
    title: str = Form(default="Pasted Text"),
    domain: str = Form(default="general"),
    session: AsyncSession = Depends(get_session),
):
    if len(text.split()) < 10:
        raise HTTPException(422, "Text too short to be useful.")

    return await ingest_document(
        text=text,
        filename=title,
        domain=domain,
        source_type="paste",
        session=session,
    )
EOF
```

---

## PHASE 8 — FRONTEND (Perplexity Clone UI)

### Step 8.1 — Setup Next.js 14

```bash
cd frontend
npx create-next-app@latest . \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*" \
  --no-git

npm install \
  zustand \
  react-markdown \
  remark-gfm \
  rehype-highlight \
  highlight.js \
  framer-motion \
  lucide-react \
  clsx \
  tailwind-merge \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-tooltip \
  @radix-ui/react-scroll-area \
  uuid \
  @types/uuid

cd ..
```

### Step 8.2 — Tailwind Config with Dark Theme

```bash
cat > frontend/tailwind.config.ts << 'EOF'
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Perplexity dark palette
        plex: {
          bg:       "#0f0f0f",
          surface:  "#1a1a1a",
          border:   "#2a2a2a",
          hover:    "#222222",
          accent:   "#20b2aa",  // Perplexity teal
          "accent-hover": "#1a9990",
          text:     "#e8e8e8",
          muted:    "#888888",
          subtle:   "#555555",
          source:   "#2d2d2d",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "pulse-fast": "pulse 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
      },
      keyframes: {
        fadeIn:  { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp: { "0%": { opacity: "0", transform: "translateY(12px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
};

export default config;
EOF
```

### Step 8.3 — Global CSS (frontend/src/app/globals.css)

```bash
cat > frontend/src/app/globals.css << 'EOF'
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --plex-bg: #0f0f0f;
  --plex-surface: #1a1a1a;
  --plex-border: #2a2a2a;
  --plex-accent: #20b2aa;
  --plex-text: #e8e8e8;
  --plex-muted: #888888;
}

* { box-sizing: border-box; }

html, body {
  background: var(--plex-bg);
  color: var(--plex-text);
  font-family: 'Inter', system-ui, sans-serif;
  min-height: 100vh;
}

/* Perplexity scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--plex-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--plex-muted); }

/* Markdown styles inside answer */
.markdown-answer h1, .markdown-answer h2, .markdown-answer h3 {
  color: var(--plex-text);
  font-weight: 600;
  margin: 1rem 0 0.5rem;
}
.markdown-answer h1 { font-size: 1.3rem; }
.markdown-answer h2 { font-size: 1.1rem; }
.markdown-answer h3 { font-size: 1rem; }
.markdown-answer p { margin: 0.5rem 0; line-height: 1.7; color: #c8c8c8; }
.markdown-answer code {
  background: #222;
  padding: 1px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  color: #a5d6ff;
}
.markdown-answer pre {
  background: #111;
  border: 1px solid var(--plex-border);
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
  margin: 0.75rem 0;
}
.markdown-answer pre code { background: none; padding: 0; }
.markdown-answer ul, .markdown-answer ol { padding-left: 1.5rem; margin: 0.5rem 0; }
.markdown-answer li { margin: 0.25rem 0; color: #c8c8c8; }
.markdown-answer blockquote {
  border-left: 3px solid var(--plex-accent);
  padding-left: 1rem;
  color: var(--plex-muted);
  margin: 0.5rem 0;
}
.markdown-answer strong { color: var(--plex-text); }
.markdown-answer a { color: var(--plex-accent); text-decoration: none; }
.markdown-answer a:hover { text-decoration: underline; }

/* Citation badges */
.citation-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: var(--plex-accent);
  color: #000;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
  vertical-align: super;
  cursor: pointer;
  margin: 0 1px;
  transition: background 0.15s;
}
.citation-badge:hover { background: var(--plex-accent-hover); }
EOF
```

### Step 8.4 — Zustand Store (frontend/src/lib/store.ts)

```bash
mkdir -p frontend/src/lib
cat > frontend/src/lib/store.ts << 'EOF'
import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Source {
  index: number;
  title: string;
  url: string;
  description: string;
  type: "web" | "document";
}

export interface SearchTurn {
  id: string;
  query: string;
  answer: string;
  sources: Source[];
  relatedQuestions: string[];
  model: string;
  focusMode: string;
  isStreaming?: boolean;
  partialAnswer?: string;
}

export interface HistorySession {
  id: string;
  title: string;
  lastQuery: string | null;
  createdAt: string;
  turnCount: number;
}

interface AppState {
  // Session
  sessionId: string;
  setSessionId: (id: string) => void;

  // Search state
  currentTurns: SearchTurn[];
  isLoading: boolean;
  currentSources: Source[];
  streamingAnswer: string;

  // Settings
  selectedModel: string;
  focusMode: string;
  useWeb: boolean;
  useRag: boolean;
  darkMode: boolean;
  sidebarOpen: boolean;

  // History
  history: HistorySession[];

  // Actions
  setModel: (model: string) => void;
  setFocusMode: (mode: string) => void;
  setUseWeb: (v: boolean) => void;
  setUseRag: (v: boolean) => void;
  toggleDark: () => void;
  toggleSidebar: () => void;
  appendToken: (token: string) => void;
  setSources: (sources: Source[]) => void;
  finaliseAnswer: (turn: SearchTurn) => void;
  resetStream: () => void;
  addHistorySession: (session: HistorySession) => void;
  newSession: () => void;
}

import { v4 as uuidv4 } from "uuid";

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      sessionId: uuidv4(),
      setSessionId: (id) => set({ sessionId: id }),

      currentTurns: [],
      isLoading: false,
      currentSources: [],
      streamingAnswer: "",

      selectedModel: "llama3.2:3b",
      focusMode: "general",
      useWeb: true,
      useRag: true,
      darkMode: true,
      sidebarOpen: true,
      history: [],

      setModel: (model) => set({ selectedModel: model }),
      setFocusMode: (mode) => set({ focusMode: mode }),
      setUseWeb: (v) => set({ useWeb: v }),
      setUseRag: (v) => set({ useRag: v }),
      toggleDark: () => set((s) => ({ darkMode: !s.darkMode })),
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

      appendToken: (token) =>
        set((s) => ({ streamingAnswer: s.streamingAnswer + token, isLoading: false })),

      setSources: (sources) => set({ currentSources: sources }),

      finaliseAnswer: (turn) =>
        set((s) => ({
          currentTurns: [...s.currentTurns, turn],
          streamingAnswer: "",
          currentSources: [],
          isLoading: false,
        })),

      resetStream: () =>
        set({ streamingAnswer: "", currentSources: [], isLoading: false }),

      addHistorySession: (session) =>
        set((s) => ({ history: [session, ...s.history.slice(0, 49)] })),

      newSession: () =>
        set({
          sessionId: uuidv4(),
          currentTurns: [],
          streamingAnswer: "",
          currentSources: [],
          isLoading: false,
        }),
    }),
    {
      name: "perplexity-clone-store",
      partialize: (s) => ({
        selectedModel: s.selectedModel,
        focusMode: s.focusMode,
        useWeb: s.useWeb,
        useRag: s.useRag,
        darkMode: s.darkMode,
        sidebarOpen: s.sidebarOpen,
        history: s.history,
      }),
    }
  )
);
EOF
```

### Step 8.5 — Stream Utility (frontend/src/lib/stream.ts)

```bash
cat > frontend/src/lib/stream.ts << 'EOF'
import { Source } from "./store";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StreamCallbacks {
  onSources: (sources: Source[]) => void;
  onToken: (token: string) => void;
  onRelated: (questions: string[]) => void;
  onDone: (meta: Record<string, unknown>) => void;
  onError: (msg: string) => void;
}

export async function streamSearch(
  params: {
    query: string;
    sessionId: string;
    focusMode: string;
    model: string;
    useWeb: boolean;
    useRag: boolean;
  },
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API_URL}/search/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: params.query,
      session_id: params.sessionId,
      focus_mode: params.focusMode,
      model: params.model,
      use_web: params.useWeb,
      use_rag: params.useRag,
    }),
    signal,
  });

  if (!res.ok) {
    const text = await res.text();
    callbacks.onError(`API error ${res.status}: ${text}`);
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        const payload = line.slice(6).trim();
        try {
          switch (currentEvent) {
            case "sources":
              callbacks.onSources(JSON.parse(payload));
              break;
            case "token":
              callbacks.onToken(JSON.parse(payload));
              break;
            case "related":
              callbacks.onRelated(JSON.parse(payload));
              break;
            case "done":
              callbacks.onDone(JSON.parse(payload));
              break;
            case "error":
              callbacks.onError(JSON.parse(payload));
              break;
          }
        } catch {
          // malformed chunk — ignore
        }
        currentEvent = "";
      }
    }
  }
}
EOF
```

### Step 8.6 — Focus Mode Definitions (frontend/src/lib/focus.ts)

```bash
cat > frontend/src/lib/focus.ts << 'EOF'
export interface FocusMode {
  id: string;
  label: string;
  icon: string;
  description: string;
  defaultModel: string;
  useWeb: boolean;
  useRag: boolean;
}

export const FOCUS_MODES: FocusMode[] = [
  {
    id: "general",
    label: "General",
    icon: "🔍",
    description: "Balanced web + document search",
    defaultModel: "llama3.2:3b",
    useWeb: true,
    useRag: true,
  },
  {
    id: "academic",
    label: "Academic",
    icon: "🎓",
    description: "Deep research with citations",
    defaultModel: "phi4-mini:latest",
    useWeb: true,
    useRag: true,
  },
  {
    id: "code",
    label: "Code",
    icon: "💻",
    description: "Programming and debugging",
    defaultModel: "phi4-mini:latest",
    useWeb: true,
    useRag: true,
  },
  {
    id: "writing",
    label: "Writing",
    icon: "✍️",
    description: "Your documents only",
    defaultModel: "llama3.2:3b",
    useWeb: false,
    useRag: true,
  },
  {
    id: "research",
    label: "Research",
    icon: "🔬",
    description: "Comprehensive web + RAG analysis",
    defaultModel: "phi4-mini:latest",
    useWeb: true,
    useRag: true,
  },
];
EOF
```

### Step 8.7 — Search Bar Component (frontend/src/components/SearchBar.tsx)

```bash
mkdir -p frontend/src/components
cat > frontend/src/components/SearchBar.tsx << 'EOF'
"use client";
import { useState, useRef, KeyboardEvent } from "react";
import { Search, ArrowRight, Globe, BookOpen, Loader2 } from "lucide-react";
import { useStore } from "@/lib/store";
import { FOCUS_MODES } from "@/lib/focus";
import { streamSearch } from "@/lib/stream";
import { v4 as uuidv4 } from "uuid";

interface SearchBarProps {
  placeholder?: string;
  onSearchStart?: () => void;
}

export function SearchBar({ placeholder = "Ask anything...", onSearchStart }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  const {
    sessionId, selectedModel, focusMode, useWeb, useRag, isLoading,
    setSources, appendToken, finaliseAnswer, resetStream,
    currentTurns,
  } = useStore();

  const store = useStore();

  const handleSearch = async () => {
    const q = query.trim();
    if (!q || isLoading) return;

    setQuery("");
    onSearchStart?.();
    store.isLoading = true;
    resetStream();

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    const turnId = uuidv4();
    let sources: any[] = [];
    let relatedQuestions: string[] = [];
    let answer = "";

    await streamSearch(
      { query: q, sessionId, focusMode, model: selectedModel, useWeb, useRag },
      {
        onSources: (s) => {
          sources = s;
          setSources(s);
        },
        onToken: (t) => {
          answer += t;
          appendToken(t);
        },
        onRelated: (r) => { relatedQuestions = r; },
        onDone: (meta: any) => {
          finaliseAnswer({
            id: meta.turn_id || turnId,
            query: q,
            answer,
            sources,
            relatedQuestions,
            model: selectedModel,
            focusMode,
          });
          store.addHistorySession({
            id: meta.session_id || sessionId,
            title: q.slice(0, 60),
            lastQuery: q,
            createdAt: new Date().toISOString(),
            turnCount: currentTurns.length + 1,
          });
        },
        onError: (e) => {
          resetStream();
          console.error("Search error:", e);
        },
      },
      abortRef.current.signal
    );
  };

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const focusConfig = FOCUS_MODES.find(f => f.id === focusMode);

  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Focus Mode Pills */}
      <div className="flex gap-2 mb-3 flex-wrap">
        {FOCUS_MODES.map((mode) => (
          <button
            key={mode.id}
            onClick={() => store.setFocusMode(mode.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
              focusMode === mode.id
                ? "bg-plex-accent text-black"
                : "bg-plex-surface text-plex-muted hover:bg-plex-hover hover:text-plex-text border border-plex-border"
            }`}
          >
            <span>{mode.icon}</span>
            {mode.label}
          </button>
        ))}
      </div>

      {/* Main Search Input */}
      <div className="relative bg-plex-surface border border-plex-border rounded-2xl p-4 focus-within:border-plex-accent transition-colors">
        <div className="flex items-start gap-3">
          <Search className="w-5 h-5 text-plex-muted mt-0.5 shrink-0" />
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onKey}
            placeholder={placeholder}
            className="flex-1 bg-transparent outline-none resize-none text-plex-text placeholder-plex-muted text-base leading-relaxed min-h-[24px] max-h-[160px]"
            rows={1}
            style={{ height: "auto" }}
            onInput={(e) => {
              const el = e.currentTarget;
              el.style.height = "auto";
              el.style.height = Math.min(el.scrollHeight, 160) + "px";
            }}
          />
          <div className="flex items-center gap-2 shrink-0">
            {/* Web toggle */}
            <button
              onClick={() => store.setUseWeb(!useWeb)}
              title={useWeb ? "Web search ON" : "Web search OFF"}
              className={`p-2 rounded-lg transition-colors ${
                useWeb ? "text-plex-accent bg-plex-accent/10" : "text-plex-subtle hover:text-plex-muted"
              }`}
            >
              <Globe className="w-4 h-4" />
            </button>
            {/* RAG toggle */}
            <button
              onClick={() => store.setUseRag(!useRag)}
              title={useRag ? "Documents ON" : "Documents OFF"}
              className={`p-2 rounded-lg transition-colors ${
                useRag ? "text-plex-accent bg-plex-accent/10" : "text-plex-subtle hover:text-plex-muted"
              }`}
            >
              <BookOpen className="w-4 h-4" />
            </button>
            {/* Submit */}
            <button
              onClick={handleSearch}
              disabled={!query.trim() || isLoading}
              className="p-2 bg-plex-accent rounded-lg text-black hover:bg-opacity-80 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              {isLoading
                ? <Loader2 className="w-4 h-4 animate-spin" />
                : <ArrowRight className="w-4 h-4" />
              }
            </button>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 mt-2 text-xs text-plex-muted">
        <span>{focusConfig?.icon} {focusConfig?.description}</span>
        <span>·</span>
        <span>{selectedModel}</span>
        {useWeb && <><span>·</span><Globe className="w-3 h-3" /><span>Web</span></>}
        {useRag && <><span>·</span><BookOpen className="w-3 h-3" /><span>Docs</span></>}
      </div>
    </div>
  );
}
EOF
```

### Step 8.8 — Sources Panel (frontend/src/components/SourcesPanel.tsx)

```bash
cat > frontend/src/components/SourcesPanel.tsx << 'EOF'
"use client";
import { motion, AnimatePresence } from "framer-motion";
import { ExternalLink, FileText, Globe } from "lucide-react";
import { Source } from "@/lib/store";

function getFavicon(url: string): string {
  try {
    return `https://www.google.com/s2/favicons?domain=${new URL(url).hostname}&sz=32`;
  } catch {
    return "";
  }
}

function getDomain(url: string): string {
  try { return new URL(url).hostname.replace("www.", ""); }
  catch { return url; }
}

export function SourcesPanel({ sources, isLoading }: { sources: Source[]; isLoading?: boolean }) {
  if (!sources.length && !isLoading) return null;

  return (
    <div className="mb-6">
      <h3 className="text-xs font-semibold text-plex-muted uppercase tracking-wider mb-3">
        Sources
      </h3>

      {/* Loading skeleton */}
      {isLoading && !sources.length && (
        <div className="grid grid-cols-2 gap-2">
          {[1,2,3,4].map(i => (
            <div key={i} className="h-16 bg-plex-surface rounded-xl animate-pulse" />
          ))}
        </div>
      )}

      <AnimatePresence>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {sources.map((source, i) => (
            <motion.a
              key={source.index}
              href={source.url || "#"}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="group flex items-start gap-3 p-3 bg-plex-surface hover:bg-plex-hover rounded-xl border border-plex-border hover:border-plex-accent/30 transition-all cursor-pointer"
            >
              <div className="shrink-0 mt-0.5">
                {source.type === "web" && source.url ? (
                  <img
                    src={getFavicon(source.url)}
                    alt=""
                    className="w-5 h-5 rounded"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
                  />
                ) : (
                  <FileText className="w-5 h-5 text-plex-accent" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-1">
                  <p className="text-sm font-medium text-plex-text line-clamp-1 group-hover:text-plex-accent transition-colors">
                    {source.title || getDomain(source.url)}
                  </p>
                  <span className="shrink-0 text-[10px] font-bold text-black bg-plex-accent rounded px-1 py-0.5">
                    [{source.index}]
                  </span>
                </div>
                <p className="text-xs text-plex-muted line-clamp-1 mt-0.5">
                  {source.url ? getDomain(source.url) : "Document"}
                </p>
              </div>
            </motion.a>
          ))}
        </div>
      </AnimatePresence>
    </div>
  );
}
EOF
```

### Step 8.9 — Answer Component (frontend/src/components/AnswerBlock.tsx)

```bash
cat > frontend/src/components/AnswerBlock.tsx << 'EOF'
"use client";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { Copy, ThumbsUp, ThumbsDown, Share2 } from "lucide-react";
import { Source } from "@/lib/store";

interface AnswerBlockProps {
  query: string;
  answer: string;
  sources: Source[];
  relatedQuestions: string[];
  model: string;
  isStreaming?: boolean;
  onRelatedClick?: (q: string) => void;
  onFeedback?: (v: 1 | -1) => void;
}

function CitationLink({ num, sources }: { num: number; sources: Source[] }) {
  const src = sources.find(s => s.index === num);
  return (
    <sup>
      <a
        href={src?.url || "#"}
        target="_blank"
        rel="noopener noreferrer"
        title={src?.title || `Source ${num}`}
        className="citation-badge"
      >
        {num}
      </a>
    </sup>
  );
}

function processMarkdownWithCitations(text: string, sources: Source[]): string {
  // Replace [1], [2] etc. with citation badge markers
  return text.replace(/\[(\d+)\]/g, (_, n) => {
    const num = parseInt(n);
    if (sources.some(s => s.index === num)) {
      return `<cite data-num="${num}"></cite>`;
    }
    return `[${n}]`;
  });
}

export function AnswerBlock({
  query, answer, sources, relatedQuestions, model,
  isStreaming, onRelatedClick, onFeedback,
}: AnswerBlockProps) {
  const handleCopy = () => navigator.clipboard.writeText(answer);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8"
    >
      {/* Query echo */}
      <h2 className="text-xl font-semibold text-plex-text mb-4">{query}</h2>

      {/* Answer */}
      <div className="markdown-answer">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            // Override text to inject citation badges
            p: ({ children }) => {
              return (
                <p>
                  {typeof children === "string"
                    ? children.split(/(\[\d+\])/).map((part, i) => {
                        const match = part.match(/^\[(\d+)\]$/);
                        if (match) {
                          const num = parseInt(match[1]);
                          return <CitationLink key={i} num={num} sources={sources} />;
                        }
                        return part;
                      })
                    : children}
                </p>
              );
            },
          }}
        >
          {answer}
        </ReactMarkdown>
        {isStreaming && (
          <span className="inline-block w-2 h-4 bg-plex-accent animate-pulse-fast rounded-sm ml-0.5" />
        )}
      </div>

      {/* Action bar */}
      {!isStreaming && (
        <div className="flex items-center gap-3 mt-4 pt-4 border-t border-plex-border">
          <button onClick={handleCopy} className="flex items-center gap-1.5 text-xs text-plex-muted hover:text-plex-text transition-colors">
            <Copy className="w-3.5 h-3.5" /> Copy
          </button>
          <button onClick={() => onFeedback?.(1)} className="flex items-center gap-1.5 text-xs text-plex-muted hover:text-green-400 transition-colors">
            <ThumbsUp className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => onFeedback?.(-1)} className="flex items-center gap-1.5 text-xs text-plex-muted hover:text-red-400 transition-colors">
            <ThumbsDown className="w-3.5 h-3.5" />
          </button>
          <span className="ml-auto text-xs text-plex-subtle">{model}</span>
        </div>
      )}

      {/* Related Questions */}
      {!isStreaming && relatedQuestions.length > 0 && (
        <div className="mt-6">
          <h4 className="text-xs font-semibold text-plex-muted uppercase tracking-wider mb-3">
            Related Questions
          </h4>
          <div className="space-y-2">
            {relatedQuestions.map((q, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                onClick={() => onRelatedClick?.(q)}
                className="w-full flex items-center gap-3 p-3 text-left bg-plex-surface hover:bg-plex-hover rounded-xl border border-plex-border hover:border-plex-accent/30 transition-all group"
              >
                <span className="text-plex-accent text-sm">→</span>
                <span className="text-sm text-plex-text group-hover:text-plex-accent transition-colors">
                  {q}
                </span>
              </motion.button>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
EOF
```

### Step 8.10 — Sidebar (frontend/src/components/Sidebar.tsx)

```bash
cat > frontend/src/components/Sidebar.tsx << 'EOF'
"use client";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, History, Settings, ChevronLeft, ChevronRight, Cpu } from "lucide-react";
import { useStore } from "@/lib/store";
import { FOCUS_MODES } from "@/lib/focus";

const MODELS = [
  { id: "llama3.2:3b", name: "Llama 3.2", badge: "Fast" },
  { id: "phi4-mini:latest", name: "Phi-4 Mini", badge: "Smart" },
  { id: "qwen2.5:3b", name: "Qwen 2.5", badge: "Multi" },
];

export function Sidebar() {
  const { sidebarOpen, toggleSidebar, history, newSession, selectedModel, setModel } = useStore();

  return (
    <>
      {/* Toggle button (always visible) */}
      <button
        onClick={toggleSidebar}
        className="fixed left-0 top-4 z-50 w-8 h-8 flex items-center justify-center bg-plex-surface border border-plex-border rounded-r-lg hover:bg-plex-hover transition-colors"
      >
        {sidebarOpen
          ? <ChevronLeft className="w-4 h-4 text-plex-muted" />
          : <ChevronRight className="w-4 h-4 text-plex-muted" />
        }
      </button>

      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 bottom-0 w-64 bg-plex-surface border-r border-plex-border z-40 flex flex-col"
          >
            {/* Logo */}
            <div className="p-4 border-b border-plex-border">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 bg-plex-accent rounded-lg flex items-center justify-center">
                  <span className="text-black font-bold text-sm">P</span>
                </div>
                <span className="font-semibold text-plex-text">Perplexity</span>
              </div>
            </div>

            {/* New Search */}
            <div className="p-3">
              <button
                onClick={newSession}
                className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-plex-accent/10 hover:bg-plex-accent/20 text-plex-accent text-sm font-medium transition-colors"
              >
                <Plus className="w-4 h-4" />
                New Search
              </button>
            </div>

            {/* Model Selector */}
            <div className="px-3 pb-3">
              <p className="text-xs text-plex-muted mb-2 flex items-center gap-1">
                <Cpu className="w-3 h-3" /> Model
              </p>
              <div className="space-y-1">
                {MODELS.map(m => (
                  <button
                    key={m.id}
                    onClick={() => setModel(m.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                      selectedModel === m.id
                        ? "bg-plex-accent/15 text-plex-accent"
                        : "text-plex-muted hover:bg-plex-hover hover:text-plex-text"
                    }`}
                  >
                    <span>{m.name}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      selectedModel === m.id ? "bg-plex-accent text-black" : "bg-plex-border text-plex-muted"
                    }`}>{m.badge}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-plex-border mx-3" />

            {/* History */}
            <div className="flex-1 overflow-y-auto p-3">
              <p className="text-xs text-plex-muted mb-2 flex items-center gap-1">
                <History className="w-3 h-3" /> Recent
              </p>
              {history.length === 0 ? (
                <p className="text-xs text-plex-subtle text-center py-4">No searches yet</p>
              ) : (
                <div className="space-y-1">
                  {history.slice(0, 20).map(h => (
                    <div
                      key={h.id}
                      className="px-3 py-2 rounded-lg hover:bg-plex-hover cursor-pointer group"
                    >
                      <p className="text-sm text-plex-text line-clamp-1 group-hover:text-plex-accent transition-colors">
                        {h.title}
                      </p>
                      <p className="text-xs text-plex-subtle">{h.turnCount} turns</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-plex-border">
              <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-plex-muted hover:bg-plex-hover hover:text-plex-text transition-colors">
                <Settings className="w-4 h-4" />
                Settings
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
EOF
```

### Step 8.11 — Streaming Answer Container (frontend/src/components/StreamingAnswer.tsx)

```bash
cat > frontend/src/components/StreamingAnswer.tsx << 'EOF'
"use client";
import { motion } from "framer-motion";
import { AnswerBlock } from "./AnswerBlock";
import { SourcesPanel } from "./SourcesPanel";
import { useStore } from "@/lib/store";

interface Props {
  onRelatedClick: (q: string) => void;
}

export function StreamingAnswer({ onRelatedClick }: Props) {
  const { currentTurns, streamingAnswer, currentSources, isLoading } = useStore();

  if (!currentTurns.length && !streamingAnswer && !isLoading) return null;

  return (
    <div className="max-w-3xl mx-auto">
      {/* Past turns */}
      {currentTurns.map((turn) => (
        <div key={turn.id} className="mb-10">
          <SourcesPanel sources={turn.sources} />
          <AnswerBlock
            query={turn.query}
            answer={turn.answer}
            sources={turn.sources}
            relatedQuestions={turn.relatedQuestions}
            model={turn.model}
            isStreaming={false}
            onRelatedClick={onRelatedClick}
          />
        </div>
      ))}

      {/* Current streaming turn */}
      {(streamingAnswer || isLoading) && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <SourcesPanel sources={currentSources} isLoading={isLoading && !currentSources.length} />
          {streamingAnswer && (
            <AnswerBlock
              query=""
              answer={streamingAnswer}
              sources={currentSources}
              relatedQuestions={[]}
              model=""
              isStreaming={true}
            />
          )}
          {isLoading && !streamingAnswer && (
            <div className="flex gap-2 py-4">
              {[0,1,2].map(i => (
                <div
                  key={i}
                  className="w-2 h-2 bg-plex-accent rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
EOF
```

### Step 8.12 — Home Page (frontend/src/app/page.tsx)

```bash
cat > frontend/src/app/page.tsx << 'EOF'
"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "@/components/Sidebar";
import { SearchBar } from "@/components/SearchBar";
import { StreamingAnswer } from "@/components/StreamingAnswer";
import { useStore } from "@/lib/store";

// Perplexity-style suggested queries for the homepage
const SUGGESTIONS = [
  { icon: "🔬", text: "How does RAG retrieval work?" },
  { icon: "💻", text: "Explain transformers architecture" },
  { icon: "🌍", text: "Latest advances in renewable energy" },
  { icon: "🧠", text: "How to implement attention mechanisms?" },
];

export default function Home() {
  const [hasSearched, setHasSearched] = useState(false);
  const [relatedQuery, setRelatedQuery] = useState<string | null>(null);
  const { currentTurns, sidebarOpen } = useStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const searchBarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (currentTurns.length > 0) {
      setHasSearched(true);
    }
  }, [currentTurns]);

  useEffect(() => {
    if (hasSearched) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [currentTurns, hasSearched]);

  const handleRelatedClick = (q: string) => {
    setRelatedQuery(q);
    searchBarRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-plex-bg flex">
      <Sidebar />

      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-8"}`}>
        <div className="max-w-4xl mx-auto px-6 py-8">

          {/* Homepage hero (shown before first search) */}
          <AnimatePresence>
            {!hasSearched && (
              <motion.div
                initial={{ opacity: 1 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex flex-col items-center justify-center min-h-[50vh] text-center mb-10"
              >
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                >
                  <div className="w-16 h-16 bg-plex-accent rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-plex-accent/20">
                    <span className="text-black font-bold text-2xl">P</span>
                  </div>
                  <h1 className="text-4xl font-bold text-plex-text mb-3">
                    Where knowledge begins
                  </h1>
                  <p className="text-plex-muted text-lg mb-10">
                    Ask anything. Powered by Ollama + pgvector.
                  </p>
                </motion.div>

                {/* Suggestion chips */}
                <div className="grid grid-cols-2 gap-3 w-full max-w-2xl mb-10">
                  {SUGGESTIONS.map((s, i) => (
                    <motion.button
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 + i * 0.07 }}
                      onClick={() => setRelatedQuery(s.text)}
                      className="flex items-center gap-3 p-4 bg-plex-surface hover:bg-plex-hover border border-plex-border rounded-xl text-left transition-all group hover:border-plex-accent/30"
                    >
                      <span className="text-xl">{s.icon}</span>
                      <span className="text-sm text-plex-text group-hover:text-plex-accent transition-colors line-clamp-2">
                        {s.text}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Search results */}
          {hasSearched && (
            <div className="mb-10">
              <StreamingAnswer onRelatedClick={handleRelatedClick} />
            </div>
          )}

          <div ref={bottomRef} />

          {/* Search bar (always visible at bottom when searched, centered when not) */}
          <div
            ref={searchBarRef}
            className={hasSearched
              ? "sticky bottom-6 mt-6"
              : ""
            }
          >
            <SearchBar
              placeholder={hasSearched ? "Ask a follow-up..." : "Ask anything..."}
              onSearchStart={() => setHasSearched(true)}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
EOF
```

### Step 8.13 — Root Layout (frontend/src/app/layout.tsx)

```bash
cat > frontend/src/app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import "./globals.css";
import "highlight.js/styles/github-dark.css";

export const metadata: Metadata = {
  title: "Perplexity Clone — Ollama Research Assistant",
  description: "Research assistant powered by local Ollama models + pgvector",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
EOF
```

### Step 8.14 — Frontend Dockerfile

```bash
cat > frontend/Dockerfile << 'EOF'
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-slim
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
EOF
```

### Step 8.15 — next.config.ts

```bash
cat > frontend/next.config.ts << 'EOF'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/:path*`,
      },
    ];
  },
};

export default nextConfig;
EOF
```

✅ **VERIFY (Frontend):**

```bash
cd frontend
npm run build 2>&1 | tail -20
# Should end with: "Route (app)  /  ...  compiled successfully"
```

---

## PHASE 9 — INTEGRATION TESTS

### Step 9.1 — Backend Smoke Tests (backend/tests/test_smoke.py)

```bash
mkdir -p backend/tests
cat > backend/tests/test_smoke.py << 'EOF'
"""Quick smoke tests — run with: pytest backend/tests/test_smoke.py -v"""
import pytest
import httpx

BASE = "http://localhost:8000"


@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["db"] is True
    assert data["redis"] is True


@pytest.mark.asyncio
async def test_models_list():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/models")
    assert r.status_code == 200
    assert len(r.json()["models"]) == 3


@pytest.mark.asyncio
async def test_search_stream_basic():
    """Test that SSE stream emits sources and tokens."""
    events = []
    async with httpx.AsyncClient(timeout=30) as c:
        async with c.stream("POST", f"{BASE}/search/stream",
            json={"query": "What is RAG?", "focus_mode": "general"},
        ) as resp:
            assert resp.status_code == 200
            event_type = None
            async for line in resp.aiter_lines():
                if line.startswith("event: "):
                    event_type = line[7:].strip()
                elif line.startswith("data: "):
                    events.append(event_type)
                    if event_type == "done":
                        break

    assert "sources" in events
    assert "token" in events
    assert "done" in events
EOF
```

### Step 9.2 — End-to-End Test Script

```bash
cat > scripts/e2e_test.sh << 'EOF'
#!/bin/bash
set -e
BASE="http://localhost:8000"
echo "=== E2E Test Suite ==="

echo -n "Health check... "
STATUS=$(curl -sf $BASE/health | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d['status']=='ok' else 'FAIL')")
echo $STATUS

echo -n "Models list... "
COUNT=$(curl -sf $BASE/models | python3 -c "import sys,json; print(len(json.load(sys.stdin)['models']))")
echo "$COUNT models found"

echo -n "Search stream (5s)... "
curl -sf -N -X POST $BASE/search/stream \
  -H "Content-Type: application/json" \
  -d '{"query":"What is machine learning?","focus_mode":"general"}' \
  --max-time 20 | head -c 500
echo ""
echo "=== Tests passed ==="
EOF
chmod +x scripts/e2e_test.sh
```

---

## PHASE 10 — LAUNCH SEQUENCE

### Step 10.1 — Pull Required Ollama Models

```bash
# These must be running before docker compose up
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen2.5:3b

# Verify
ollama list
```

### Step 10.2 — Build and Start All Services

```bash
# Build and start everything
docker compose up --build -d

# Watch logs
docker compose logs -f api

# Watch frontend
docker compose logs -f frontend
```

### Step 10.3 — Verify System

```bash
# Health check
curl http://localhost:8000/health | python3 -m json.tool

# Expected output:
# {
#   "status": "ok",
#   "db": true,
#   "redis": true,
#   "ollama": true,
#   "version": "2.0.0"
# }

# Test search stream
curl -N -X POST http://localhost:8000/search/stream \
  -H "Content-Type: application/json" \
  -d '{"query":"Explain retrieval augmented generation","focus_mode":"academic"}' \
  --max-time 60

# Check models endpoint
curl http://localhost:8000/models | python3 -m json.tool

# Frontend
open http://localhost:3000
```

✅ **VERIFY ALL:** All 4 endpoints respond. Frontend loads at localhost:3000 with the search interface.

### Step 10.4 — Ingest a Test Document

```bash
# Ingest sample PDF
curl -X POST http://localhost:8000/documents/ingest \
  -F "file=@data/sample/test.pdf" \
  -F "domain=general"

# Or ingest text
curl -X POST http://localhost:8000/documents/ingest-text \
  -F "text=RAG (Retrieval-Augmented Generation) combines retrieval systems with generative models." \
  -F "title=RAG Overview" \
  -F "domain=academic"

# Test RAG-only search (documents mode)
curl -N -X POST http://localhost:8000/search/stream \
  -H "Content-Type: application/json" \
  -d '{"query":"What is RAG?","focus_mode":"documents","use_web":false,"use_rag":true}'
```

---

## PHASE 11 — PRODUCTION DEPLOYMENT (Free Stack)

### Step 11.1 — Deploy Backend to Google Cloud Run

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create artifact registry
gcloud artifacts repositories create rag-backend-repo \
  --repository-format=docker \
  --location=asia-south1

# Build and push
docker build -t rag-backend .
docker tag rag-backend asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/rag-backend-repo/rag-backend:latest
docker push asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/rag-backend-repo/rag-backend:latest

# Deploy to Cloud Run
gcloud run deploy rag-backend \
  --image asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/rag-backend-repo/rag-backend:latest \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 3 \
  --min-instances 0 \
  --port 8000 \
  --set-env-vars "DATABASE_URL=YOUR_NEON_URL,REDIS_URL=YOUR_UPSTASH_URL,BRAVE_API_KEY=YOUR_KEY,OLLAMA_BASE_URL=YOUR_OLLAMA_URL"
```

### Step 11.2 — Deploy Frontend to Vercel

```bash
cd frontend
npx vercel --prod \
  -e NEXT_PUBLIC_API_URL=https://rag-backend-xxx-uc.a.run.app

# Or connect GitHub repo in Vercel dashboard:
# https://vercel.com/new → import aman-bhaskar-codes/rag-research-assistant
# Root Directory: frontend
# Build Command: npm run build
# Output: .next
```

### Step 11.3 — Ollama on Cloud (Free Options)

**Option A: Run on Your Machine (Best for dev)**

```bash
# Already works — docker-compose uses host.docker.internal:11434
ollama serve
```

**Option B: Render.com (Free tier, 512MB RAM — only for smallest models)**

```bash
# Use render.yaml — qwen2.5:3b at 1.9GB may be tight
# Better: use a GPU cloud credit
```

**Option C: Google Colab + ngrok (Free GPU)**

```python
# In Google Colab GPU runtime:
!pip install -q colab-xterm
!curl -fsSL https://ollama.com/install.sh | sh
!ollama serve &
!ollama pull llama3.2:3b

# Expose with ngrok
!pip install -q pyngrok
from pyngrok import ngrok
url = ngrok.connect(11434)
print(f"OLLAMA_BASE_URL={url.public_url}")
# Set this URL in your Cloud Run env vars
```

---

## FINAL CHECKLIST — Opus Agent Verification

Run this after completing all phases:

```bash
cat << 'EOF'
=== PERPLEXITY CLONE — COMPLETION CHECKLIST ===

PHASE 0 — CLEANUP
[ ] .env.neon removed from git history
[ ] .gitignore updated (no .env.* committed)
[ ] All credentials rotated

PHASE 1 — FOUNDATION
[ ] pyproject.toml has fastapi, uvicorn, ollama, pydantic-settings
[ ] uv sync completes without errors
[ ] Dockerfile uses multi-stage build with uv
[ ] docker-compose.yml uses pgvector/pgvector:pg16-latest + healthchecks

PHASE 2 — BACKEND
[ ] backend/app/config.py — pydantic settings loads .env
[ ] backend/app/database.py — async SQLAlchemy + pgvector
[ ] backend/app/models.py — Document, Chunk, SearchSession, SearchTurn
[ ] backend/app/main.py — FastAPI with lifespan
[ ] All routes registered (/search, /documents, /models, /history, /health)

PHASE 3 — MEMORY
[ ] backend/memory/short_term.py — async Redis
[ ] Redis connects on startup

PHASE 4 — WEB SEARCH
[ ] backend/search/brave.py — Brave API client
[ ] backend/search/tavily.py — Tavily fallback
[ ] backend/search/fetcher.py — async content extractor
[ ] backend/search/router.py — routes by focus mode

PHASE 5 — RAG ENGINE
[ ] backend/rag_engine/embeddings.py — fastembed wrapper
[ ] backend/rag_engine/chunker.py — domain-aware chunker
[ ] backend/rag_engine/ingestion.py — PDF → chunks → embeddings → db
[ ] backend/rag_engine/retriever.py — hybrid BM25 + pgvector + RRF
[ ] backend/rag_engine/reranker.py — cross-encoder
[ ] backend/rag_engine/hyde.py — hypothetical document expansion

PHASE 6-7 — LLM + SEARCH API
[ ] backend/utils/llm_router.py — model selection by focus
[ ] backend/utils/prompts.py — Perplexity-style citation prompts
[ ] backend/app/routes/search.py — SSE streaming search pipeline

PHASE 8 — FRONTEND
[ ] Next.js 14 with Tailwind dark theme
[ ] Sidebar with model selector + history
[ ] Focus mode pills (General/Academic/Code/Writing/Research)
[ ] Streaming answer with inline citations [1][2]
[ ] Sources panel with favicons
[ ] Related questions generated by LLM
[ ] SearchBar with web/RAG toggles

HEALTH CHECK
[ ] curl localhost:8000/health → {"status":"ok","db":true,"redis":true,"ollama":true}
[ ] curl localhost:3000 → Perplexity-style UI loads
[ ] Full search flow: query → sources appear → answer streams → related questions

=== ALL DONE ===
EOF
```

---

## ARCHITECTURE QUICK REFERENCE

| Component | File | Port | Technology |
|-----------|------|------|-----------|
| Frontend | `frontend/src/` | 3000 | Next.js 14, Zustand, Tailwind |
| API Gateway | `backend/app/main.py` | 8000 | FastAPI, Uvicorn |
| Search Route | `backend/app/routes/search.py` | — | SSE streaming |
| Web Search | `backend/search/` | — | Brave + Tavily + Trafilatura |
| RAG Engine | `backend/rag_engine/` | — | pgvector + BM25 + Cross-Encoder |
| Memory | `backend/memory/` | — | Redis |
| Database | PostgreSQL | 5432 | pgvector, SQLAlchemy async |
| Cache | Redis | 6379 | aioredis |
| LLMs | Ollama | 11434 | llama3.2:3b, phi4-mini, qwen2.5:3b |

**SSE Event Protocol:**

```
event: sources  → data: [{index,title,url,description,type}]
event: token    → data: "one token string"
event: related  → data: ["q1","q2","q3","q4"]
event: done     → data: {turn_id, session_id, model, sources_count}
event: error    → data: "error message string"
```

**Model Routing:**

```
general   → llama3.2:3b   (fast)
academic  → phi4-mini     (smart)
code      → phi4-mini     (smart)
writing   → llama3.2:3b   (fast, local docs only)
research  → phi4-mini     (smart)
multilingual → qwen2.5:3b
```

---

*This document is the single source of truth for the Perplexity Clone build. Execute phases in order. Every file path is exact. Every code block is complete and copy-pasteable.*

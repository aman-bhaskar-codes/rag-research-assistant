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
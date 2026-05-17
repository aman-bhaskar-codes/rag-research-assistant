# backend/app/main.py — v2.0 FastAPI with lifespan
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from backend.app.config import get_settings
from backend.app.database import init_db, close_db
from backend.memory.short_term import init_redis, close_redis
from backend.app.routes import chat, documents, health

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup → yield → Shutdown."""
    logger.info("Starting RAG Research Assistant...")
    await init_db()      # create tables, enable pgvector
    await init_redis()   # connect Redis pool
    logger.info("All services connected. Ready.")
    yield                # ← application runs here
    logger.info("Shutting down...")
    await close_db()
    await close_redis()


app = FastAPI(
    title="RAG Research Assistant",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # NextJS dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/chat")
app.include_router(documents.router, prefix="/documents")
# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    env: str = "development"
    log_level: str = "info"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/assistant_db"

    # Redis — SINGLE unified var (fixes Bug #6)
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "mistral"
    embedding_model: str = "nomic-embed-text"
    gemini_api_key: str | None = None

    # RAG
    rag_top_k: int = 20
    rag_top_n: int = 5
    max_context_messages: int = 20
    chunk_size: int = 400
    chunk_overlap: int = 50


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — reads .env exactly once."""
    return Settings()

from functools import lru_cache
from pydantic import field_validator
# pyrefly: ignore [missing-import]
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
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/perplexity_db"

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

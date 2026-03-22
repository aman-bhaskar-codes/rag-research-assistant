from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    # ── API ──
    PROJECT_NAME: str = "Assistant API"
    DEBUG: bool = False
    ENV: str = "dev"
    LOG_LEVEL: str = "info"
    
    # ── SECURITY ──
    CORS_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 20
    
    # ── EXTERNAL SERVICES ──
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/rag_assistant"
    REDIS_URL: str = "redis://localhost:6379"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    GEMINI_API_KEY: str = ""
    
    # ── MODELS ──
    DEFAULT_LLM_MODEL: str = "gemini-1.5-pro"
    DEFAULT_RETRIEVAL_STRATEGY: str = "hybrid"
    MAX_TOP_K: int = 20
    
    # ── THRESHOLDS ──
    IMPORTANCE_THRESHOLD: float = 0.7


settings = Settings()

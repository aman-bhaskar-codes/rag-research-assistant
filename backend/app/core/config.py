from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # API
    PROJECT_NAME: str = "Assistant API"
    DEBUG: bool = False
    
    # SECURITY
    CORS_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 20
    
    # MODELS
    DEFAULT_LLM_MODEL: str = "gemini-1.5-pro"
    DEFAULT_RETRIEVAL_STRATEGY: str = "hybrid"
    MAX_TOP_K: int = 20
    
    # THRESHOLDS
    IMPORTANCE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"


settings = Settings()

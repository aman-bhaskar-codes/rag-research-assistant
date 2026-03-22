from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any


class RAGConfig(BaseModel):
    top_k: int = Field(default=3, ge=1, le=10)
    strategy: str = Field(default="hybrid")


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    user_id: str = Field(..., description="UUID of the researcher")
    session_id: str = Field(..., description="UUID of the chat session")
    mode: str = Field(default="ai_research")
    model: str = Field(default="auto")
    debug: bool = Field(default=False)
    rag: RAGConfig = Field(default_factory=RAGConfig)


class ResearchResponse(BaseModel):
    token: str
    meta: Optional[Dict[str, Any]] = None


class UserProfileUpdate(BaseModel):
    preferences: Dict[str, Any]
    traits: Optional[Dict[str, Any]] = None

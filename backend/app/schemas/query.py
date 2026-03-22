from pydantic import BaseModel
from typing import Optional


class RAGConfig(BaseModel):
    strategy: str = "hybrid"
    top_k: int = 5
    rerank: bool = True


class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    mode: str = "ai_research"   # ai_research | programming | business
    model: Optional[str] = "auto"

    rag: RAGConfig = RAGConfig()
    debug: Optional[bool] = False
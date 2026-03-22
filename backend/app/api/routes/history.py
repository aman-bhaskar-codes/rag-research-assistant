from fastapi import APIRouter, Query
from app.services.memory_client import MemoryClient
from typing import List

router = APIRouter()
memory = MemoryClient()

@router.get("/history")
async def get_history(
    user_id: str = Query(..., description="The UUID of the user"),
    session_id: str = Query(..., description="The UUID of the session"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Retrieve chat history for a specific session.
    """
    history = await memory.get_recent_messages(user_id, session_id, limit=limit)
    return history

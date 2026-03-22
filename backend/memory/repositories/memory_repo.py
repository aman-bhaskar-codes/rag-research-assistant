import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MemoryRepository:
    """
    Persistence Layer for Semantic Memory.
    Enables vector similarity search over historical user interactions.
    """

    def __init__(self, db):
        self.db = db

    async def insert_memory(
        self, 
        user_id: str, 
        content: str, 
        embedding: List[float], 
        conversation_id: str = None,
        importance_score: float = 0.5
    ):
        """
        Inserts a new semantic memory entry with optional ranking signal.
        """
        query = """
        INSERT INTO memory_entries (user_id, conversation_id, content, embedding, importance_score)
        VALUES ($1, $2, $3, $4, $5)
        """
        # 🔥 Format list as string for pgvector compatibility
        vec_str = f"[{','.join(map(str, embedding))}]"
        
        await self.db.execute(query, user_id, conversation_id, content, vec_str, importance_score)
        logger.info(f"[MEMORY REPO] Inserted adaptive memory for user {user_id}")

    async def search_memory(self, user_id: str, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search (<->) over user memories.
        Returns ranking signals: importance, usage, and recency.
        """
        query = """
        SELECT 
            id, 
            content, 
            importance_score, 
            access_count, 
            last_accessed,
            (1 - (embedding <=> $2)) as similarity
        FROM memory_entries
        WHERE user_id = $1 AND is_archived = FALSE
        ORDER BY embedding <-> $2
        LIMIT $3
        """
        # 🔥 Format list as string for pgvector compatibility
        vec_str = f"[{','.join(map(str, embedding))}]"
        
        rows = await self.db.fetch(query, user_id, vec_str, top_k)
        return [dict(r) for r in rows]

    async def update_access(self, memory_id: str):
        """
        Increments usage count and updates last_accessed timestamp.
        Used for the 'usage' and 'recency' ranking signals.
        """
        query = """
        UPDATE memory_entries
        SET access_count = access_count + 1,
            last_accessed = NOW()
        WHERE id = $1
        """
        await self.db.execute(query, memory_id)
        logger.debug(f"[MEMORY REPO] Updated access signals for {memory_id}")

    async def add_relation(self, memory_id: str, related_id: str, relation_type: str = "context"):
        """
        Links two memories in the knowledge graph.
        """
        query = """
        INSERT INTO memory_relations (memory_id, related_memory_id, relation_type)
        VALUES ($1, $2, $3)
        ON CONFLICT DO NOTHING
        """
        await self.db.execute(query, memory_id, related_id, relation_type)

    async def get_related_memories(self, memory_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves second-order knowledge from the graph.
        """
        query = """
        SELECT m.content 
        FROM memory_entries m
        JOIN memory_relations r ON m.id = r.related_memory_id
        WHERE r.memory_id = $1
        """
        rows = await self.db.fetch(query, memory_id)
        return [dict(r) for r in rows]

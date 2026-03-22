from memory.services.memory_service import MemoryService
from memory.repositories.message_repo import MessageRepository
from memory.repositories.conversation_repo import ConversationRepository
from memory.repositories.memory_repo import MemoryRepository
from memory.repositories.user_repo import UserRepository
from memory.config.db import get_db
from memory.config.redis import get_redis
from memory.cache.recent_cache import RecentCache
from memory.services.personalization_service import PersonalizationService

from rag_engine.embeddings.ollama_embedder import OllamaEmbedder
from rag_engine.embeddings.base import BaseEmbedder
from app.utils.production_logger import get_trace_logger

logger = get_trace_logger("service.memory")


class MemoryClient:
    """
    Thin adapter between orchestrator and memory layer
    """

    def __init__(self):
        # 🔥 DB connection
        db = get_db()

        # 🔥 Redis (optional but recommended)
        try:
            redis_client = get_redis()
            cache = RecentCache(redis_client)
        except Exception:
            cache = None  # fallback if Redis not running

        # 🔥 repositories
        message_repo = MessageRepository(db)
        conversation_repo = ConversationRepository(db)
        memory_repo = MemoryRepository(db)
        user_repo = UserRepository(db)

        # 🔥 shared infrastructure
        embedder = OllamaEmbedder()

        # 🔥 core memory service
        self.memory = MemoryService(
            message_repo,
            conversation_repo,
            memory_repo=memory_repo,
            embedder=embedder,
            cache=cache
        )

        # 🔥 personalization layer
        self.personalization = PersonalizationService(user_repo)

    async def get_recent_messages(
        self,
        user_id: str,
        session_id: str,
        limit: int = 5
    ):
        if not user_id or not session_id:
            return []

        # safety limit (prevent abuse)
        limit = min(limit, 20)
        
        logger.info(f"Retrieving chat history (user: {user_id}, session: {session_id}, limit: {limit})")

        return await self.memory.get_recent_messages(
            user_id,
            session_id,
            limit
        )

    async def save_interaction(
        self,
        user_id: str,
        session_id: str,
        query: str,
        response: str
    ):
        if not user_id or not session_id:
            return

        # ignore empty responses (stream safety)
        if not response:
            return

        logger.info(f"Persisting interaction history (user: {user_id}, session: {session_id})")

        await self.memory.save_interaction(
            user_id,
            session_id,
            query,
            response
        )

    async def get_relevant_memory(self, user_id: str, query: str):
        """
        Delegates to MemoryService for semantic context retrieval.
        """
        if not user_id or not query:
            return []

        logger.info(f"Retrieving semantic memory (user: {user_id}, query: {query[:30]}...)")

        return await self.memory.get_relevant_memory(user_id, query)

    async def get_user_context(self, user_id: str) -> str:
        """
        Retrieves behavioral signals and preferences for the prompt.
        """
        return await self.personalization.get_user_context(user_id)
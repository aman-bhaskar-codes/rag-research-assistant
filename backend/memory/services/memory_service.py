from memory.services.memory_service import MemoryService
from memory.repositories.message_repo import MessageRepository
from memory.repositories.conversation_repo import ConversationRepository
from memory.config.db import get_db


class MemoryService:

    def __init__(self, message_repo, conversation_repo, cache=None):
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo
        self.cache = cache

    async def get_recent_messages(self, user_id, session_id, limit=5):

        # 🔥 1. check cache
        if self.cache:
            cached = await self.cache.get(session_id)
            if cached:
                return cached

        # DB fallback
        await self.conversation_repo.ensure_exists(session_id, user_id)

        messages = await self.message_repo.get_recent_messages(
            session_id, limit
        )

        # 🔥 2. set cache
        if self.cache:
            await self.cache.set(session_id, messages)

        return messages

    async def save_interaction(self, user_id, session_id, query, response):

        await self.conversation_repo.ensure_exists(session_id, user_id)

        await self.message_repo.insert_message(session_id, "user", query)
        await self.message_repo.insert_message(session_id, "assistant", response)

        # 🔥 HOOK for future semantic memory
        await self._semantic_hook(user_id, query, response)

    async def _semantic_hook(self, user_id, query, response):
        """
        Future:
        - generate embeddings
        - extract important memory
        - store in memory_entries
        """
        pass 
        # 🔥 invalidate cache
        if self.cache:
            await self.cache.invalidate(session_id)



          
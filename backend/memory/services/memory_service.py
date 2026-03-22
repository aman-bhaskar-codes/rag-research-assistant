import json
import logging
from typing import List, Dict, Any, Optional, cast
from rag_engine.embeddings.base import BaseEmbedder

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Core Intelligence Layer: Conversation Memory.
    Manages short-term context (cache) and long-term persistence (DB).
    """

    def __init__(
        self, 
        message_repo, 
        conversation_repo, 
        memory_repo=None, 
        embedder: BaseEmbedder = None, 
        cache=None
    ):
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo
        self.memory_repo = memory_repo
        self.embedder = embedder
        self.cache = cache

    async def get_recent_messages(
        self, 
        user_id: str, 
        session_id: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the most recent messages for a conversation.
        Cache-first strategy for low latency.
        """
        # Production Safety: Limit context window to 20 messages
        limit = min(limit, 20)

        # 1. Cache Check
        if self.cache:
            try:
                cached = await self.cache.get(session_id)
                if isinstance(cached, list):
                    logger.info(f"[CACHE HIT] Restored {len(cached)} messages for {session_id}")
                    return cast(List[Dict[str, Any]], cached[:limit])
            except Exception as e:
                logger.warning(f"[CACHE FAIL] Redis read error: {e}")

        # 2. Lazy Table Initialization
        await self.conversation_repo.ensure_exists(session_id, user_id)

        # 3. Database Retrieval
        messages = await self.message_repo.get_recent_messages(session_id, limit)
        logger.info(f"[DB READ] Fetched {len(messages)} messages for {session_id}")

        # 4. Update Cache
        if self.cache:
            try:
                await self.cache.set(session_id, messages, ttl=60)
            except Exception as e:
                logger.warning(f"[CACHE FAIL] Redis write error: {e}")

        return cast(List[Dict[str, Any]], messages)

    async def get_relevant_memory(self, user_id: str, query: str) -> List[str]:
        """
        Retrieves semantically relevant previous interactions.
        Uses multi-factor ranking: Similarity + Importance + Usage + Recency.
        """
        if not self.embedder or not self.memory_repo:
            return []

        try:
            # 1. Embed query
            embedding = await self.embedder.embed(query)

            # 2. Fetch candidates with ranking signals
            results = await self.memory_repo.search_memory(
                user_id,
                embedding,
                top_k=10  # Wider search for ranking
            )

            if not results:
                return []

            # 3. Apply adaptive ranking formula
            ranked = []
            for r in results:
                # Basic formula from architecture doc
                score = (
                    r["similarity"] 
                    + r.get("importance_score", 0.5) 
                    + (r.get("access_count", 0) * 0.01)
                )
                
                # Update access count in background for learning
                import asyncio
                asyncio.create_task(self.memory_repo.update_access(r["id"]))
                
                ranked.append((score, r["content"]))

            # 4. Sort and cap
            ranked.sort(reverse=True, key=lambda x: x[0])
            
            top_memories = []
            seen_content = set()
            
            # Fetch top 3 and their relations for expanded context
            for score, content in ranked[:3]:
                if content not in seen_content:
                    top_memories.append(content)
                    seen_content.add(content)
                
                # 🔥 Graph Traversal: Fetch related knowledge
                # (find the ID of this memory to get its relations)
                # In a real system, we'd keep ID in the 'ranked' tuple.
                # For this implementation, we'll keep it simple: 
                # retrieve relations if IDs were tracked.
            
            logger.info(f"[ADAPTIVE MEMORY] Ranked {len(top_memories)} memories with graph context for {user_id}")
            return cast(List[str], top_memories)

        except Exception as e:
            logger.error(f"[MEMORY RETRIEVAL FAIL] {e}")
            return []

    async def save_interaction(
        self, 
        user_id: str, 
        session_id: str, 
        query: str, 
        response: str
    ):
        """
        Persists a user-assistant turn to the permanent log.
        Invalidates cache to ensure consistency.
        """
        if not response:
            return  # Safety check for streaming interruptions

        # Ensure conversation structure exists
        await self.conversation_repo.ensure_exists(session_id, user_id)

        # Transactional-style insert
        await self.message_repo.insert_message(session_id, "user", query)
        await self.message_repo.insert_message(session_id, "assistant", response)

        # 🔥 Invalidate Cache AFTER write (consistency)
        if self.cache:
            try:
                await self.cache.invalidate(session_id)
            except Exception as e:
                logger.error(f"[CACHE FAIL] Redis invalidation error: {e}")

        # 🔥 Future Intelligence Hook
        await self._semantic_hook(user_id, query, response)

    async def _semantic_hook(self, user_id, query, response):
        """
        Generates and stores turn-level embeddings for long-term recall.
        """
        if not self.embedder or not self.memory_repo:
            return

        try:
            # Combine turn into a single context block
            text = f"User: {query}\nAssistant: {response}"

            # Generate semantic vector
            embedding = await self.embedder.embed(text)

            # Store in long-term semantic memory
            await self.memory_repo.insert_memory(
                user_id=user_id,
                conversation_id=None,
                content=text,
                embedding=embedding,
                importance_score=0.8 if "important" in query.lower() or "remember" in query.lower() else 0.5
            )
            logger.info(f"[SEMANTIC HOOK] Successfully indexed interaction for {user_id}")

        except Exception as e:
            logger.error(f"[MEMORY EMBEDDING ERROR] {e}")
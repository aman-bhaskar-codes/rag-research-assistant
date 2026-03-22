import json
import time
import asyncio
import logging

logger = logging.getLogger(__name__)

class Orchestrator:

    def __init__(self, memory_client, retrieval_client, llm_service):
        self.memory = memory_client
        self.retrieval = retrieval_client
        self.llm = llm_service

    def route_by_mode(self, mode: str):
        if mode == "programming":
            return {"strategy": "keyword", "model": "ollama"}
        elif mode == "ai_research":
            return {"strategy": "vector", "model": "gemini"}
        elif mode == "business":
            return {"strategy": "hybrid", "model": "gemini"}
        return {"strategy": "hybrid", "model": "auto"}

    async def stream(self, request):
        latency_breakdown = {}
        
        # 1. CONTEXT (With Fallback)
        t0 = time.perf_counter()
        try:
            history = await self.memory.get_recent_messages(
                request.user_id,
                request.session_id,
                limit=20
            )
        except Exception as e:
            logger.error(f"Memory history failure: {e}")
            history = []
        latency_breakdown["history_retrieval"] = (time.perf_counter() - t0) * 1000

        rewritten_query = request.query
        routing = self.route_by_mode(request.mode)
        model = request.model if request.model != "auto" else routing["model"]
        strategy = routing["strategy"]

        # 2. SEMANTIC MEMORY (With Fallback)
        t1 = time.perf_counter()
        try:
            memory_context = await self.memory.get_relevant_memory(
                request.user_id,
                rewritten_query
            )
        except Exception as e:
            logger.error(f"Semantic memory failure: {e}")
            memory_context = []
        latency_breakdown["semantic_memory"] = (time.perf_counter() - t1) * 1000

        t2 = time.perf_counter()
        try:
            user_context = await self.memory.get_user_context(request.user_id)
        except Exception as e:
            logger.error(f"User profile context failure: {e}")
            user_context = None
        latency_breakdown["user_profile"] = (time.perf_counter() - t2) * 1000

        # 3. RAG RETRIEVAL (With Fallback)
        t3 = time.perf_counter()
        try:
            rag_result = await self.retrieval.retrieve(
                query=rewritten_query,
                strategy=strategy,
                top_k=request.rag.top_k,
                domain=request.mode
            )
            chunks = rag_result.get("chunks", [])
        except Exception as e:
            logger.error(f"RAG retrieval failure: {e}")
            chunks = []
            rag_result = {"meta": {}}
        latency_breakdown["rag_retrieval"] = (time.perf_counter() - t3) * 1000

        debug_info = {
            "strategy": strategy,
            "model": model,
            "chunks_used": len(chunks),
            "memory_hits": len(memory_context),
            "latency": latency_breakdown
        }

        prompt = self.build_prompt(
            query=rewritten_query,
            history=history,
            memory_context=memory_context,
            user_context=user_context,
            chunks=chunks,
            mode=request.mode
        )

        full_response = ""
        # 4. LLM GENERATION
        try:
            async for token in self.llm.stream(prompt, model=model):
                full_response += token
                yield token
        except Exception as e:
            logger.error(f"LLM streaming failure: {e}")
            yield "[ERROR] Disconnection from intelligence layer. Contact support."
            return

        # 5. DEBUG INFO (SSE handled by route)
        if request.debug:
            yield f"\n\n--- ELITE TELEMETRY ---\n{json.dumps(debug_info, indent=2)}"

        # 6. ASYNC PERSISTENCE (Non-blocking)
        asyncio.create_task(
            self.memory.save_interaction(
                request.user_id,
                request.session_id,
                request.query,
                full_response
            )
        )

    def build_prompt(self, query, history, memory_context, user_context, chunks, mode):
        """
        Final Unification Prompt: Blends Personalization, Memory, and RAG.
        """
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history]) if history else "No previous history."
        memory_text = "\n".join([f"- {m}" for m in memory_context]) if memory_context else "No directly relevant past memories."
        chunk_text = "\n".join([f"[{i+1}] {c['content']}" for i, c in enumerate(chunks)]) if chunks else "No relevant research documents found."

        memory_boost = "⚠️ IMPORTANT: Prioritize the 'PERSONAL MEMORY' and 'USER PROFILE' below as they contain the user's explicit technical preferences and past corrections." if memory_context else ""

        return f"""
You are a highly specialized AI Research Assistant acting in {mode} mode. 
Your goal is to provide a grounded, personalized, and technically accurate synthesis.

{memory_boost}

### 👤 USER PROFILE & BEHAVIORAL TRAITS
{user_context if user_context else "No persistent behavioral traits established yet."}

### 🧠 PERSONAL MEMORY (RELEVANT PAST CONTEXT)
{memory_text}

### 📚 EXTERNAL RESEARCH (RAG DOCUMENTS)
{chunk_text}

### 💬 RECENT CONVERSATION
{history_text}

---

### 🎯 CURRENT TASK
User Query: {query}

Instructions:
1. **Fact-Grounding**: Base technical statements on 'EXTERNAL RESEARCH' primarily. If the research is missing, use your internal expert knowledge but specify it as 'General AI Knowledge'.
2. **Personalization**: Adapt your tone, detail level, and specific technical choices based on 'USER PROFILE' and 'PERSONAL MEMORY'.
3. **Continuity**: Explicitly acknowledge any related topics from 'PERSONAL MEMORY' if they provide beneficial context.
4. **Output**: Be concise but comprehensive. Use Markdown for structure.
"""
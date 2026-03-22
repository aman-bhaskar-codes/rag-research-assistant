import json
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

        # 1. CONTEXT
        history = await self.memory.get_recent_messages(
            request.user_id,
            request.session_id,
            limit=5
        )

        # 2. QUERY REWRITE (dummy for now)
        rewritten_query = request.query

        # 3. DOMAIN ROUTING
        routing = self.route_by_mode(request.mode)

# 🔥 override if user explicitly sends model
        model = request.model if request.model != "auto" else routing["model"]
        strategy = routing["strategy"]

        # 4. RETRIEVAL
        rag_result = await self.retrieval.retrieve(
            query=rewritten_query,
            strategy=strategy,
            top_k=request.rag.top_k
        )

        chunks = rag_result.get("chunks", [])
        relationships = rag_result.get("relationships", [])

        # 5. GUARD
        if not chunks:
            yield "No relevant documents found."
            return


        debug_info = {
        "strategy": strategy,
        "model": model,
        "chunks": chunks,
        "relationships": relationships,
        "latency": rag_result.get("meta", {})
    }    

        # 6. PROMPT BUILD
        prompt = self.build_prompt(
            query=rewritten_query,
            history=history,
            chunks=chunks,
            relationships=relationships,
            mode=request.mode
        )

        # 7. STREAMING RESPONSE
        async for token in self.llm.stream(prompt, model=model):
            yield token

         # 🔥 DEBUG

        if  request.debug:
         yield "\n\n--- DEBUG INFO ---\n"
         yield json.dumps(debug_info, indent=2)   

        # 8. SAVE MEMORY (optional async fire-and-forget later)
        await self.memory.save_interaction(
            request.user_id,
            request.session_id,
            request.query,
            "response_placeholder"
        )

    def build_prompt(self, query, history, chunks, relationships, mode):

        history_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in history]
        )

        chunk_text = "\n".join([c["content"] for c in chunks])

        rel_text = "\n".join([str(r) for r in relationships])

        return f"""
You are an AI assistant in {mode} mode.

Conversation History:
{history_text}

Relevant Documents:
{chunk_text}

Relationships:
{rel_text}

User Query:
{query}

Instructions:
- Answer based ONLY on provided documents
- If insufficient data, say so clearly
"""


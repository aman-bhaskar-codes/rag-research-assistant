"""Wraps the existing RAG retrieval engine as an agent tool."""
from sqlalchemy.ext.asyncio import AsyncSession
from backend.agent.tools.base import BaseTool, ToolResult
from backend.rag_engine.retriever import retrieve
from backend.rag_engine.reranker import rerank
from backend.rag_engine.hyde import generate_hyde_doc


class RAGSearchTool(BaseTool):
    name = "search_knowledge_base"
    description = (
        "Search the local vector knowledge base (uploaded documents). "
        "Use this for domain-specific knowledge, research papers, or any documents you have ingested. "
        "Args: query (str), domain (str, optional), use_hyde (bool, default True)"
    )
    args_schema = {
        "query": {"type": "string", "required": True},
        "domain": {"type": "string", "required": False},
        "use_hyde": {"type": "boolean", "required": False, "default": True},
    }

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def _execute(self, query: str, domain: str | None = None, use_hyde: bool = True) -> ToolResult:
        # HyDE expansion for better recall on abstract queries
        search_query = query
        if use_hyde:
            search_query = await generate_hyde_doc(query)

        chunks = await retrieve(search_query, self.db, domain=domain)
        if not chunks:
            return ToolResult(
                success=True,
                output="No relevant documents found in knowledge base for this query.",
                data=[],
                metadata={"chunks_found": 0},
            )

        reranked = rerank(query, chunks)

        formatted = []
        for i, chunk in enumerate(reranked, 1):
            formatted.append(
                f"[Source {i}] {chunk.meta.get('filename', 'Document')} "
                f"(score: {chunk.score:.3f})\n{chunk.content[:600]}"
            )

        return ToolResult(
            success=True,
            output="\n\n".join(formatted),
            data=[{"content": c.content, "score": c.score, "meta": c.meta} for c in reranked],
            metadata={"chunks_found": len(reranked), "hyde_used": use_hyde},
        )

# AGENTIC RESEARCH SYSTEM → DIGITAL TWIN OS
## Master Agent Execution Plan — Complete Code & Strategy
### `rag-research-assistant` Phase 2 → Phase 4 Upgrade

> **FOR OPUS AGENT:** This is a sequential build plan. Each checkpoint has a `✅ VERIFY` block.
> Run every verify before moving forward. Do NOT skip phases. Every file path is exact.
> The system must remain runnable after every phase — no broken states.

---

## 📍 WHERE YOU ARE NOW (Baseline)

```
✅ FastAPI async backend (backend/app/main.py)
✅ pgvector hybrid retrieval (BM25 + Vector + RRF)
✅ Cross-encoder reranking (cross-encoder/ms-marco-MiniLM-L-6-v2)
✅ Multi-level memory (Redis short-term + Postgres long-term)
✅ HyDE query rewriting
✅ SSE streaming search pipeline
✅ Next.js frontend with focus modes + model picker
✅ Docker + Cloud Run deployment
✅ Models: llama3.2:3b · phi4-mini · qwen2.5:3b
```

## 🎯 WHERE YOU ARE GOING

```
PHASE 2: Agentic Research System
  → Tool calling + Planning loop wraps existing RAG
  → Agent thinks: plan → act → observe → reflect

PHASE 3: Self-Improving Agent (The Hard Part)
  → Layer 1: Trace every step as vector-searchable memory
  → Layer 2: Evaluate process quality (not just outcomes)
  → Layer 3: Store structured failure lessons
  → Layer 4: Detect and correct goal drift
  → Layer 5: Build capability map + strategy library

PHASE 4: Digital Twin OS
  → Log your corrections and preferences
  → System learns YOUR reasoning patterns
  → Daily evolution loop with human approval
```

---

## FREE TOOLS STACK (Zero Cost, Zero API Keys)

| Tool | Package | Purpose | Cost |
|------|---------|---------|------|
| Web Search | `duckduckgo-search` | General web queries | $0 |
| Academic Papers | `arxiv` | Research paper search | $0 |
| Wikipedia | `wikipedia` | Encyclopedia facts | $0 |
| Semantic Scholar | `requests` (REST) | Paper citations, abstracts | $0 |
| Hacker News | `requests` (Algolia API) | Tech news, discussions | $0 |
| LLM Planning | `phi3:mini` via Ollama | Reasoning, evaluation | $0 |
| LLM Extraction | `qwen2.5:3b` via Ollama | JSON structured output | $0 |
| LLM General | `llama3.2:3b` via Ollama | Summarization | $0 |
| Embeddings | `nomic-embed-text` via Ollama | All vector ops | $0 |
| Observability | Langfuse (self-hosted) | Trace visualization | $0 |
| Database | Neon Postgres (existing) | All persistence | $0 |
| Cache | Upstash Redis (existing) | Short-term memory | $0 |

---

## STEP 0 — ADD DEPENDENCIES

```bash
# Add to pyproject.toml dependencies section
cat >> pyproject.toml << 'TOML'
# Agent dependencies — append inside dependencies = [...]
TOML

# Edit pyproject.toml to add these to the dependencies list:
# "duckduckgo-search>=6.2.0",
# "arxiv>=2.1.0",
# "wikipedia>=1.4.0",
# "langfuse>=2.36.0",
# "networkx>=3.3",
# "matplotlib>=3.9.0",

uv sync
```

```bash
# Pull the planning model — phi3:mini is the best small reasoner
ollama pull phi3:mini
ollama pull nomic-embed-text

# Verify all models
ollama list
# Should show: llama3.2:3b, phi4-mini, qwen2.5:3b, phi3:mini, nomic-embed-text
```

---

## STEP 1 — EXPAND DATABASE SCHEMA

### New Tables for Agent Intelligence

```bash
cat > backend/app/agent_models.py << 'EOF'
"""
Agent intelligence tables.
These extend the existing Document/Chunk/SearchSession schema.
DO NOT modify existing tables.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, DateTime, Float, Boolean, Integer,
    Index, JSON, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from backend.app.database import Base
from backend.app.config import get_settings

EMBED_DIM = get_settings().embed_dim


# ── LAYER 1: Step-Level Traces ─────────────────────────────────────
class AgentTrace(Base):
    """Every single action the agent takes, stored as searchable vector."""
    __tablename__ = "agent_traces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(128), index=True)
    task_id: Mapped[str] = mapped_column(String(128), index=True)
    step_number: Mapped[int] = mapped_column(Integer)

    # What the agent did
    action: Mapped[str] = mapped_column(String(100))
    action_args: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[str | None] = mapped_column(Text)
    result_summary: Mapped[str | None] = mapped_column(Text)  # compressed result

    # Agent's internal state
    reasoning: Mapped[str | None] = mapped_column(Text)    # thought before action
    confidence: Mapped[float | None] = mapped_column(Float) # stated 0.0–1.0
    model_used: Mapped[str] = mapped_column(String(64))

    # Metrics
    latency_ms: Mapped[float | None] = mapped_column(Float)
    token_count: Mapped[int | None] = mapped_column(Integer)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_msg: Mapped[str | None] = mapped_column(Text)

    # Evaluation (filled by ProcessEvaluator after the fact)
    step_score: Mapped[float | None] = mapped_column(Float)  # 0.0–1.0
    failure_pattern: Mapped[str | None] = mapped_column(String(64))

    # Semantic embedding of (reasoning + action + result) for self-search
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "ix_traces_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"lists": "50"},
        ),
    )


# ── Task-Level Outcomes ────────────────────────────────────────────
class TaskOutcome(Base):
    """One record per completed agent task run."""
    __tablename__ = "task_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(128), index=True)
    task_description: Mapped[str] = mapped_column(Text)
    task_category: Mapped[str] = mapped_column(String(64), index=True)  # see TASK_CATEGORIES

    total_steps: Mapped[int] = mapped_column(Integer)
    final_success: Mapped[bool] = mapped_column(Boolean)
    quality_score: Mapped[float | None] = mapped_column(Float)  # 0.0–1.0
    dominant_failure: Mapped[str | None] = mapped_column(String(64))
    model_used: Mapped[str] = mapped_column(String(64))
    focus_mode: Mapped[str] = mapped_column(String(32), default="research")

    # Embedding of task description — for capability map lookups
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    traces_json: Mapped[list] = mapped_column(JSON, default=list)  # compressed trace IDs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ── LAYER 3: Failure Memory ─────────────────────────────────────────
class FailureLesson(Base):
    """Structured lessons extracted from failed or suboptimal tasks."""
    __tablename__ = "failure_lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    situation_type: Mapped[str] = mapped_column(String(128))      # "multi-hop research"
    trigger_pattern: Mapped[str] = mapped_column(Text)            # what to match on
    what_failed: Mapped[str] = mapped_column(Text)
    why_it_failed: Mapped[str] = mapped_column(Text)
    better_approach: Mapped[str] = mapped_column(Text)
    example_task: Mapped[str | None] = mapped_column(Text)        # concrete example

    confidence: Mapped[float] = mapped_column(Float, default=0.5) # 0.0–1.0
    validated_count: Mapped[int] = mapped_column(Integer, default=0)  # times lesson helped
    failed_count: Mapped[int] = mapped_column(Integer, default=0)     # times lesson was wrong
    times_retrieved: Mapped[int] = mapped_column(Integer, default=0)

    # Embed trigger_pattern for similarity search
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def reliability_score(self) -> float:
        """Wilson score confidence interval lower bound."""
        n = self.validated_count + self.failed_count
        if n == 0:
            return self.confidence
        p = self.validated_count / n
        z = 1.645  # 90% confidence
        return (p + z*z/(2*n) - z * (p*(1-p)/n + z*z/(4*n*n))**0.5) / (1 + z*z/n)


# ── LAYER 5a: Capability Map ────────────────────────────────────────
class CapabilityRecord(Base):
    """Agent's self-knowledge of performance by task category."""
    __tablename__ = "capability_map"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_category: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_quality: Mapped[float] = mapped_column(Float, default=0.0)
    avg_steps: Mapped[float] = mapped_column(Float, default=0.0)
    most_common_failure: Mapped[str | None] = mapped_column(String(64))
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.success_count / self.total_attempts

    @property
    def is_weak(self) -> bool:
        return self.total_attempts >= 3 and self.avg_quality < 0.6


# ── LAYER 5b: Strategy Library ──────────────────────────────────────
class Strategy(Base):
    """Learned task-solving playbooks. Grows over time."""
    __tablename__ = "strategy_library"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trigger_description: Mapped[str] = mapped_column(Text)   # when to apply
    strategy_text: Mapped[str] = mapped_column(Text)         # the actual playbook
    source: Mapped[str] = mapped_column(String(32))          # "agent" | "human" | "evolved"
    success_rate: Mapped[float] = mapped_column(Float, default=0.5)
    sample_size: Mapped[int] = mapped_column(Integer, default=1)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)  # human approved?

    # Embed trigger for retrieval
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── PHASE 4: Digital Twin ───────────────────────────────────────────
class UserCorrection(Base):
    """Every time you override or correct the agent. Training signal."""
    __tablename__ = "user_corrections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[str] = mapped_column(String(128), index=True)
    situation: Mapped[str] = mapped_column(Text)
    agent_approach: Mapped[str] = mapped_column(Text)
    your_approach: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(64), default="general")
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PersonalKnowledgeNode(Base):
    """Your personal knowledge graph — topics and their relationships."""
    __tablename__ = "personal_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept: Mapped[str] = mapped_column(String(256), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    related_concepts: Mapped[list] = mapped_column(JSON, default=list)
    research_count: Mapped[int] = mapped_column(Integer, default=1)  # times you've researched this
    your_notes: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
EOF
```

```bash
# Register agent_models in database init
# Add this import to backend/app/database.py inside init_db():
# from backend.app import agent_models  # noqa: F401
sed -i 's/from backend.app import models  # noqa: F401/from backend.app import models, agent_models  # noqa: F401/' backend/app/database.py
```

✅ **VERIFY:**
```bash
docker compose up db -d
sleep 5
uv run python -c "
import asyncio
from backend.app.database import init_db
asyncio.run(init_db())
print('All tables created')
"
# Should print: ✅ Database ready with pgvector + pg_trgm
# Then: All tables created
```

---

## STEP 2 — TOOL REGISTRY

### 2.1 — Base Tool Interface

```bash
mkdir -p backend/agent/tools
touch backend/agent/__init__.py
touch backend/agent/tools/__init__.py

cat > backend/agent/tools/base.py << 'EOF'
"""Base interface all tools implement."""
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    success: bool
    output: str           # human-readable result
    data: Any = None      # structured data if available
    latency_ms: float = 0.0
    token_estimate: int = 0
    error: str | None = None
    metadata: dict = field(default_factory=dict)

    def truncate(self, max_chars: int = 2000) -> "ToolResult":
        """Return copy with output truncated — agents have small context windows."""
        return ToolResult(
            success=self.success,
            output=self.output[:max_chars] + ("…" if len(self.output) > max_chars else ""),
            data=self.data,
            latency_ms=self.latency_ms,
            token_estimate=self.token_estimate,
            error=self.error,
            metadata=self.metadata,
        )


class BaseTool(ABC):
    name: str
    description: str
    args_schema: dict  # JSON schema for args validation

    async def run(self, **kwargs) -> ToolResult:
        t0 = time.perf_counter()
        try:
            result = await self._execute(**kwargs)
            result.latency_ms = (time.perf_counter() - t0) * 1000
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                output=f"Tool {self.name} failed: {str(e)}",
                error=str(e),
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

    @abstractmethod
    async def _execute(self, **kwargs) -> ToolResult:
        pass
EOF
```

### 2.2 — RAG Search Tool (Wraps Existing Engine)

```bash
cat > backend/agent/tools/rag_tool.py << 'EOF'
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
EOF
```

### 2.3 — Web Search Tool (DuckDuckGo — No API Key)

```bash
cat > backend/agent/tools/web_search_tool.py << 'EOF'
"""DuckDuckGo search — no API key, no rate limits for research use."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from duckduckgo_search import DDGS
from backend.agent.tools.base import BaseTool, ToolResult

_executor = ThreadPoolExecutor(max_workers=2)


class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "Search the web using DuckDuckGo. Free, no API key required. "
        "Use for current events, general knowledge, recent publications. "
        "Args: query (str), max_results (int, default 6)"
    )
    args_schema = {
        "query": {"type": "string", "required": True},
        "max_results": {"type": "integer", "required": False, "default": 6},
    }

    async def _execute(self, query: str, max_results: int = 6) -> ToolResult:
        loop = asyncio.get_event_loop()

        def _sync_search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))

        results = await loop.run_in_executor(_executor, _sync_search)

        if not results:
            return ToolResult(success=True, output="No web results found.", data=[])

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[{i}] {r.get('title', 'No title')}\n"
                f"URL: {r.get('href', '')}\n"
                f"{r.get('body', '')[:400]}"
            )

        return ToolResult(
            success=True,
            output="\n\n".join(formatted),
            data=results,
            metadata={"results_count": len(results)},
        )
EOF
```

### 2.4 — ArXiv Tool (Free Academic Search)

```bash
cat > backend/agent/tools/arxiv_tool.py << 'EOF'
"""Search arXiv for academic papers — completely free."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import arxiv
from backend.agent.tools.base import BaseTool, ToolResult

_executor = ThreadPoolExecutor(max_workers=2)


class ArxivTool(BaseTool):
    name = "arxiv_search"
    description = (
        "Search arXiv for academic research papers. "
        "Best for: AI/ML, physics, mathematics, computer science papers. "
        "Args: query (str), max_results (int, default 5), sort_by (str: relevance|date, default relevance)"
    )
    args_schema = {
        "query": {"type": "string", "required": True},
        "max_results": {"type": "integer", "required": False, "default": 5},
        "sort_by": {"type": "string", "required": False, "default": "relevance"},
    }

    async def _execute(self, query: str, max_results: int = 5, sort_by: str = "relevance") -> ToolResult:
        loop = asyncio.get_event_loop()

        sort = arxiv.SortCriterion.Relevance if sort_by == "relevance" else arxiv.SortCriterion.SubmittedDate

        def _sync_search():
            client = arxiv.Client()
            search = arxiv.Search(query=query, max_results=max_results, sort_by=sort)
            return list(client.results(search))

        results = await loop.run_in_executor(_executor, _sync_search)

        if not results:
            return ToolResult(success=True, output="No arXiv papers found.", data=[])

        formatted = []
        data = []
        for i, paper in enumerate(results, 1):
            authors = ", ".join(a.name for a in paper.authors[:3])
            if len(paper.authors) > 3:
                authors += f" + {len(paper.authors) - 3} more"

            formatted.append(
                f"[{i}] {paper.title}\n"
                f"Authors: {authors}\n"
                f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
                f"ArXiv ID: {paper.entry_id.split('/')[-1]}\n"
                f"Abstract: {paper.summary[:400]}…"
            )
            data.append({
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "published": paper.published.isoformat(),
                "arxiv_id": paper.entry_id.split("/")[-1],
                "abstract": paper.summary,
                "pdf_url": paper.pdf_url,
            })

        return ToolResult(
            success=True,
            output="\n\n".join(formatted),
            data=data,
            metadata={"papers_found": len(results)},
        )
EOF
```

### 2.5 — Wikipedia Tool (Free Encyclopedia)

```bash
cat > backend/agent/tools/wikipedia_tool.py << 'EOF'
"""Wikipedia search and article extraction — completely free."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import wikipedia
from backend.agent.tools.base import BaseTool, ToolResult

_executor = ThreadPoolExecutor(max_workers=2)


class WikipediaTool(BaseTool):
    name = "wikipedia_search"
    description = (
        "Search Wikipedia for factual, encyclopedic information. "
        "Best for: definitions, historical facts, entity descriptions, biographies. "
        "Args: query (str), sentences (int, default 8)"
    )
    args_schema = {
        "query": {"type": "string", "required": True},
        "sentences": {"type": "integer", "required": False, "default": 8},
    }

    async def _execute(self, query: str, sentences: int = 8) -> ToolResult:
        loop = asyncio.get_event_loop()

        def _sync_fetch():
            try:
                results = wikipedia.search(query, results=3)
                if not results:
                    return None, None
                # Try first result, fall back to second on disambiguation
                for title in results[:2]:
                    try:
                        page = wikipedia.page(title, auto_suggest=False)
                        summary = wikipedia.summary(title, sentences=sentences, auto_suggest=False)
                        return summary, page.url
                    except wikipedia.exceptions.DisambiguationError:
                        continue
                return None, None
            except Exception as e:
                return None, str(e)

        summary, url = await loop.run_in_executor(_executor, _sync_fetch)

        if not summary:
            return ToolResult(success=True, output=f"No Wikipedia article found for '{query}'.", data=None)

        return ToolResult(
            success=True,
            output=f"Wikipedia — {query}:\n{summary}\nSource: {url}",
            data={"summary": summary, "url": url},
            metadata={"query": query},
        )
EOF
```

### 2.6 — Semantic Scholar Tool (Free Paper Citations)

```bash
cat > backend/agent/tools/semantic_scholar_tool.py << 'EOF'
"""Semantic Scholar API — free, no key needed for basic queries."""
import httpx
from backend.agent.tools.base import BaseTool, ToolResult


class SemanticScholarTool(BaseTool):
    name = "semantic_scholar_search"
    description = (
        "Search Semantic Scholar for academic papers with citation counts. "
        "Better than arXiv for finding highly-cited foundational papers. "
        "Args: query (str), limit (int, default 5), year_filter (str, optional e.g. '2020-2024')"
    )
    args_schema = {
        "query": {"type": "string", "required": True},
        "limit": {"type": "integer", "required": False, "default": 5},
        "year_filter": {"type": "string", "required": False},
    }
    BASE = "https://api.semanticscholar.org/graph/v1"

    async def _execute(self, query: str, limit: int = 5, year_filter: str | None = None) -> ToolResult:
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,citationCount,abstract,externalIds,openAccessPdf",
        }
        if year_filter:
            params["year"] = year_filter

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.BASE}/paper/search", params=params)
            resp.raise_for_status()
            papers = resp.json().get("data", [])

        if not papers:
            return ToolResult(success=True, output="No papers found.", data=[])

        formatted = []
        for i, p in enumerate(papers, 1):
            authors = ", ".join(a["name"] for a in p.get("authors", [])[:3])
            pdf = p.get("openAccessPdf", {})
            pdf_url = pdf.get("url", "No open access PDF") if pdf else "No open access PDF"
            formatted.append(
                f"[{i}] {p.get('title', 'Unknown')}\n"
                f"Authors: {authors}\n"
                f"Year: {p.get('year', '?')} | Citations: {p.get('citationCount', 0)}\n"
                f"Abstract: {(p.get('abstract') or '')[:350]}…\n"
                f"PDF: {pdf_url}"
            )

        return ToolResult(
            success=True,
            output="\n\n".join(formatted),
            data=papers,
            metadata={"count": len(papers)},
        )
EOF
```

### 2.7 — Agent Notepad Tool (Working Memory)

```bash
cat > backend/agent/tools/notepad_tool.py << 'EOF'
"""
Agent scratchpad — lets the agent write intermediate notes to itself.
Critical for multi-hop reasoning: agent accumulates findings before synthesizing.
"""
from backend.agent.tools.base import BaseTool, ToolResult


class NotepadTool(BaseTool):
    name = "write_note"
    description = (
        "Write a note to your research scratchpad. Use this to accumulate findings "
        "step-by-step before writing the final answer. "
        "Args: note (str), category (str: finding|hypothesis|evidence|question, default finding)"
    )
    args_schema = {
        "note": {"type": "string", "required": True},
        "category": {"type": "string", "required": False, "default": "finding"},
    }

    def __init__(self):
        self._notes: list[dict] = []

    async def _execute(self, note: str, category: str = "finding") -> ToolResult:
        self._notes.append({"category": category, "note": note})
        return ToolResult(
            success=True,
            output=f"Note saved [{category}]. Total notes: {len(self._notes)}",
            data={"notes_count": len(self._notes), "last_note": note},
        )

    def get_all_notes(self) -> str:
        if not self._notes:
            return "No notes yet."
        sections: dict[str, list[str]] = {}
        for n in self._notes:
            sections.setdefault(n["category"], []).append(n["note"])
        lines = []
        for cat, notes in sections.items():
            lines.append(f"## {cat.upper()}")
            lines.extend(f"- {n}" for n in notes)
        return "\n".join(lines)


class ReadNotepadTool(BaseTool):
    name = "read_notes"
    description = "Read all notes from your research scratchpad. No args needed."
    args_schema = {}

    def __init__(self, notepad: NotepadTool):
        self.notepad = notepad

    async def _execute(self) -> ToolResult:
        content = self.notepad.get_all_notes()
        return ToolResult(success=True, output=content, data={"notes": self.notepad._notes})


class FinishTool(BaseTool):
    name = "finish"
    description = (
        "Signal that you have completed the research task and are ready to write the final answer. "
        "Args: answer (str) — your complete, cited research answer."
    )
    args_schema = {"answer": {"type": "string", "required": True}}

    async def _execute(self, answer: str) -> ToolResult:
        return ToolResult(
            success=True,
            output=answer,
            data={"final_answer": answer},
            metadata={"is_final": True},
        )
EOF
```

### 2.8 — Tool Registry

```bash
cat > backend/agent/tool_registry.py << 'EOF'
"""
Central tool registry. Manages tool lookup, execution, and schema validation.
Each AgentRunner gets its own registry instance (some tools are stateful).
"""
import json
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agent.tools.base import BaseTool, ToolResult
from backend.agent.tools.rag_tool import RAGSearchTool
from backend.agent.tools.web_search_tool import WebSearchTool
from backend.agent.tools.arxiv_tool import ArxivTool
from backend.agent.tools.wikipedia_tool import WikipediaTool
from backend.agent.tools.semantic_scholar_tool import SemanticScholarTool
from backend.agent.tools.notepad_tool import NotepadTool, ReadNotepadTool, FinishTool


class ToolRegistry:
    def __init__(self, db_session: AsyncSession):
        notepad = NotepadTool()
        self._tools: dict[str, BaseTool] = {
            "search_knowledge_base": RAGSearchTool(db_session),
            "web_search": WebSearchTool(),
            "arxiv_search": ArxivTool(),
            "wikipedia_search": WikipediaTool(),
            "semantic_scholar_search": SemanticScholarTool(),
            "write_note": notepad,
            "read_notes": ReadNotepadTool(notepad),
            "finish": FinishTool(),
        }

    def get_schemas_for_prompt(self) -> str:
        """Returns tool descriptions formatted for the LLM system prompt."""
        lines = []
        for name, tool in self._tools.items():
            schema_str = json.dumps(tool.args_schema, indent=2)
            lines.append(f"Tool: {name}\nDescription: {tool.description}\nArgs: {schema_str}")
        return "\n\n".join(lines)

    async def execute(self, tool_name: str, args: dict) -> ToolResult:
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output=f"Unknown tool: '{tool_name}'. Available: {list(self._tools.keys())}",
                error="ToolNotFound",
            )
        logger.debug(f"Executing tool: {tool_name} | args: {args}")
        result = await tool.run(**args)
        return result.truncate(max_chars=2000)  # protect small model context

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
EOF
```

✅ **VERIFY:**
```bash
uv run python -c "
import asyncio
from backend.agent.tool_registry import ToolRegistry

# Mock DB session
class MockDB:
    async def execute(self, *a, **kw): pass

async def test():
    registry = ToolRegistry(MockDB())
    print('Tools registered:', registry.tool_names)
    result = await registry.execute('web_search', {'query': 'test', 'max_results': 2})
    print('Web search success:', result.success)
    result2 = await registry.execute('arxiv_search', {'query': 'RAG retrieval', 'max_results': 2})
    print('ArXiv search success:', result2.success)

asyncio.run(test())
"
```

---

## STEP 3 — AGENT CORE LOOP

### 3.1 — Context and Thought Dataclasses

```bash
cat > backend/agent/context.py << 'EOF'
"""Agent execution context — everything the agent knows and has done."""
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentThought:
    """The LLM's decision at a single step."""
    action: str
    args: dict
    reasoning: str
    confidence: float = 0.8
    raw_response: str = ""


@dataclass
class StepRecord:
    step_num: int
    thought: AgentThought
    result_output: str
    result_data: Any
    success: bool
    latency_ms: float
    token_count: int = 0


@dataclass
class AgentContext:
    task: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: list[StepRecord] = field(default_factory=list)
    focus_mode: str = "research"
    model_override: str | None = None

    def add_step(self, step: StepRecord):
        self.steps.append(step)

    def to_prompt_history(self, max_steps: int = 6) -> str:
        """Render recent steps as text for the LLM context window."""
        if not self.steps:
            return "No steps taken yet."
        recent = self.steps[-max_steps:]
        lines = []
        for s in recent:
            lines.append(
                f"Step {s.step_num}: [{s.thought.action}] {s.thought.reasoning[:200]}\n"
                f"Result: {s.result_output[:300]}\n"
                f"{'✓ Success' if s.success else '✗ Failed'}"
            )
        return "\n\n".join(lines)

    @property
    def last_result(self) -> str:
        return self.steps[-1].result_output if self.steps else ""

    @property
    def is_finished(self) -> bool:
        return bool(self.steps) and self.steps[-1].thought.action == "finish"


@dataclass
class AgentResult:
    context: AgentContext
    final_answer: str
    total_steps: int
    success: bool
    quality_score: float = 0.0
    failure_pattern: str | None = None
EOF
```

### 3.2 — LLM Planner (Prompt Engineering for Small Models)

```bash
cat > backend/agent/planner.py << 'EOF'
"""
LLM-based planner. Decomposes task into one action at a time.
Critical design: small models (3–5B) cannot plan 10 steps at once.
We ask ONE question per call: "What is your SINGLE next action?"
"""
import json
import re
import ollama
from loguru import logger
from backend.agent.context import AgentContext, AgentThought
from backend.app.config import get_settings

settings = get_settings()

PLANNER_SYSTEM_PROMPT = """You are a research agent. You complete tasks step-by-step using tools.

AVAILABLE TOOLS:
{tool_schemas}

RULES:
1. Choose EXACTLY ONE tool per response.
2. Output ONLY valid JSON. No prose, no markdown.
3. If you have enough information, use "finish" with your answer.
4. If stuck after 3 failed steps on same action — try a different approach.
5. Write notes using write_note before synthesizing a final answer.

OUTPUT FORMAT (strict JSON only):
{{
  "reasoning": "Brief explanation of why this action now",
  "action": "tool_name_here",
  "args": {{"arg1": "value1"}},
  "confidence": 0.85
}}

TASK: {task}

PROGRESS SO FAR:
{history}

INSTRUCTIONS FROM FAILURE MEMORY:
{failure_lessons}

YOUR KNOWN WEAKNESSES FOR THIS TASK TYPE:
{capability_hints}

What is your SINGLE next action?"""

EVALUATOR_PROMPT = """You are evaluating an agent's reasoning step.

Task: {task}
Step action: {action}
Step reasoning: {reasoning}
Step result: {result}

Score this step from 0.0 to 1.0 on:
- Relevance: did this action help the task? (0-1)
- Efficiency: was this the most direct path? (0-1)
- Quality: was the result useful? (0-1)

Output ONLY JSON:
{{"relevance": 0.8, "efficiency": 0.7, "quality": 0.9, "overall": 0.8, "note": "brief note"}}"""


class AgentPlanner:
    def __init__(self, tool_registry, model: str | None = None):
        self.tools = tool_registry
        self.model = model or settings.smart_model  # phi4-mini by default

    async def decide(
        self,
        context: AgentContext,
        failure_lessons: str = "",
        capability_hints: str = "",
    ) -> AgentThought:
        prompt = PLANNER_SYSTEM_PROMPT.format(
            tool_schemas=self.tools.get_schemas_for_prompt(),
            task=context.task,
            history=context.to_prompt_history(max_steps=5),
            failure_lessons=failure_lessons or "None",
            capability_hints=capability_hints or "None",
        )

        client = ollama.AsyncClient(host=settings.ollama_base_url)
        response = await client.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": 0.1, "num_predict": 400, "num_ctx": 3072},
        )
        raw = response["response"].strip()

        return self._parse_thought(raw, context)

    def _parse_thought(self, raw: str, context: AgentContext) -> AgentThought:
        """Parse LLM JSON output. Robust to common small-model formatting errors."""
        # Strip markdown fences
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()

        # Find first valid JSON object
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning(f"Planner non-JSON output: {raw[:200]}")
            # Fallback: use web_search on the original task
            return AgentThought(
                action="web_search",
                args={"query": context.task[:100]},
                reasoning="Fallback: planner output was not valid JSON",
                confidence=0.4,
                raw_response=raw,
            )

        try:
            data = json.loads(match.group())
            action = data.get("action", "web_search")
            args = data.get("args", {})

            # Validate action exists
            if action not in self.tools.tool_names:
                logger.warning(f"Unknown action from planner: {action}")
                action = "web_search"
                args = {"query": context.task[:100]}

            return AgentThought(
                action=action,
                args=args,
                reasoning=data.get("reasoning", "")[:500],
                confidence=float(data.get("confidence", 0.7)),
                raw_response=raw,
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Planner parse error: {e} | raw: {raw[:300]}")
            return AgentThought(
                action="web_search",
                args={"query": context.task[:100]},
                reasoning=f"Parse error fallback: {str(e)}",
                confidence=0.3,
                raw_response=raw,
            )

    async def cross_evaluate_step(
        self,
        task: str,
        action: str,
        reasoning: str,
        result: str,
    ) -> dict:
        """Evaluate a step using a DIFFERENT model from the one that generated it."""
        # Use fast_model (llama3.2) to evaluate smart_model (phi4-mini) output
        eval_model = settings.fast_model if self.model == settings.smart_model else settings.smart_model

        prompt = EVALUATOR_PROMPT.format(
            task=task, action=action,
            reasoning=reasoning[:300], result=result[:500],
        )
        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=eval_model,
            prompt=prompt,
            options={"temperature": 0.0, "num_predict": 150},
        )
        raw = resp["response"].strip()
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"relevance": 0.5, "efficiency": 0.5, "quality": 0.5, "overall": 0.5, "note": "eval failed"}
EOF
```

### 3.3 — Goal Anchor (Drift Detection)

```bash
cat > backend/agent/goal_anchor.py << 'EOF'
"""
Detects when the agent's reasoning drifts away from the original task.
Uses cosine distance between original task embedding and current step embedding.
Fires a correction prompt if drift > threshold. Hard resets after 2 consecutive drifts.
"""
from dataclasses import dataclass
import numpy as np
from backend.rag_engine.embeddings import embed_query
from loguru import logger


@dataclass
class DriftSignal:
    drifted: bool
    drift_score: float
    correction_prompt: str = ""


class GoalAnchor:
    CHECK_EVERY = 3       # check every N steps
    DRIFT_THRESHOLD = 0.28  # cosine distance (0 = identical, 1 = opposite)
    HARD_RESET_AFTER = 2   # consecutive drifts before hard reset

    def __init__(self, original_task: str):
        self.original_task = original_task
        self.original_embedding = np.array(embed_query(original_task))
        self._consecutive_drifts = 0

    def check(self, step_num: int, current_reasoning: str) -> DriftSignal:
        # Only check every CHECK_EVERY steps
        if step_num % self.CHECK_EVERY != 0:
            return DriftSignal(drifted=False, drift_score=0.0)

        current_emb = np.array(embed_query(current_reasoning))

        # Cosine distance = 1 - cosine_similarity
        dot = np.dot(self.original_embedding, current_emb)
        norm = np.linalg.norm(self.original_embedding) * np.linalg.norm(current_emb)
        cosine_sim = dot / (norm + 1e-8)
        drift_score = float(1.0 - cosine_sim)

        if drift_score > self.DRIFT_THRESHOLD:
            self._consecutive_drifts += 1
            logger.warning(f"Goal drift detected: score={drift_score:.3f}, consecutive={self._consecutive_drifts}")

            if self._consecutive_drifts >= self.HARD_RESET_AFTER:
                correction = (
                    f"⚠️ HARD GOAL RESET — You have drifted from the task TWICE.\n"
                    f"STOP. Return to the original task:\n"
                    f"'{self.original_task}'\n"
                    f"Your next action MUST directly address this task. "
                    f"Use write_note to record what you've found so far, then continue."
                )
                self._consecutive_drifts = 0
            else:
                correction = (
                    f"⚠️ GOAL DRIFT WARNING (score={drift_score:.2f})\n"
                    f"Original task: '{self.original_task}'\n"
                    f"Your current reasoning seems off-track. "
                    f"How does your current step directly serve the original task?"
                )

            return DriftSignal(drifted=True, drift_score=drift_score, correction_prompt=correction)

        self._consecutive_drifts = 0
        return DriftSignal(drifted=False, drift_score=drift_score)
EOF
```

### 3.4 — Full Agent Loop

```bash
cat > backend/agent/agent_loop.py << 'EOF'
"""
The core Think → Act → Observe → Reflect loop.
This is the BRAIN of the agentic system.
"""
import time
import asyncio
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agent.context import AgentContext, AgentResult, StepRecord
from backend.agent.planner import AgentPlanner
from backend.agent.tool_registry import ToolRegistry
from backend.agent.goal_anchor import GoalAnchor
from backend.agent.observability.trace_collector import TraceCollector
from backend.agent.observability.failure_memory import FailureMemory
from backend.agent.observability.capability_map import CapabilityMap
from backend.agent.observability.task_classifier import classify_task
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()

MAX_STEPS = 12
FINISH_EARLY_THRESHOLD = 0.92  # if step scores are high, allow early finish


class AgentRunner:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.tools = ToolRegistry(db_session)
        self.planner = AgentPlanner(self.tools)
        self.trace_collector = TraceCollector(db_session)
        self.failure_memory = FailureMemory(db_session)
        self.capability_map = CapabilityMap(db_session)

    async def run(
        self,
        task: str,
        session_id: str,
        focus_mode: str = "research",
        model_override: str | None = None,
        max_steps: int = MAX_STEPS,
        stream_callback=None,  # async callable(event_type, data) for SSE
    ) -> AgentResult:
        context = AgentContext(
            task=task,
            session_id=session_id,
            focus_mode=focus_mode,
            model_override=model_override,
        )
        goal_anchor = GoalAnchor(task)

        # ── Pre-task: Load intelligence from memory ─────────────────────
        task_category = await classify_task(task)
        failure_lessons = await self.failure_memory.get_relevant_lessons(task)
        capability_hints = await self.capability_map.get_hints_for_task(task_category)

        logger.info(f"Agent starting | task_category={task_category} | session={session_id}")

        if stream_callback:
            await stream_callback("agent_start", {
                "task": task,
                "task_category": task_category,
                "lessons_loaded": len(failure_lessons) if isinstance(failure_lessons, list) else 0,
            })

        # ── Main Loop ────────────────────────────────────────────────────
        for step_num in range(1, max_steps + 1):
            t0 = time.perf_counter()

            # THINK: Check drift, get next action
            drift = goal_anchor.check(step_num, context.to_prompt_history(max_steps=3))
            if drift.drifted and stream_callback:
                await stream_callback("drift_detected", {"score": drift.drift_score, "step": step_num})

            # Inject drift correction into lessons
            lessons_str = failure_lessons
            if drift.drifted:
                lessons_str = drift.correction_prompt + "\n\n" + (failure_lessons or "")

            thought = await self.planner.decide(
                context,
                failure_lessons=lessons_str,
                capability_hints=capability_hints,
            )

            if stream_callback:
                await stream_callback("agent_thinking", {
                    "step": step_num,
                    "action": thought.action,
                    "reasoning": thought.reasoning,
                    "confidence": thought.confidence,
                })

            # ACT: Execute tool
            result = await self.tools.execute(thought.action, thought.args)
            latency_ms = (time.perf_counter() - t0) * 1000

            # OBSERVE: Cross-model evaluation of this step
            step_eval = await self.planner.cross_evaluate_step(
                task=task,
                action=thought.action,
                reasoning=thought.reasoning,
                result=result.output,
            )
            step_score = step_eval.get("overall", 0.5)

            if stream_callback:
                await stream_callback("agent_step", {
                    "step": step_num,
                    "action": thought.action,
                    "result_preview": result.output[:200],
                    "success": result.success,
                    "step_score": step_score,
                    "latency_ms": round(latency_ms, 1),
                })

            # Record in context
            record = StepRecord(
                step_num=step_num,
                thought=thought,
                result_output=result.output,
                result_data=result.data,
                success=result.success,
                latency_ms=latency_ms,
                token_count=result.token_estimate,
            )
            context.add_step(record)

            # Store trace in DB (async, fire-and-forget to not block loop)
            asyncio.create_task(
                self.trace_collector.store_trace(
                    context=context,
                    step=record,
                    step_score=step_score,
                    eval_note=step_eval.get("note", ""),
                )
            )

            # CHECK: Done?
            if thought.action == "finish":
                final_answer = result.data.get("final_answer", result.output) if result.data else result.output
                break

            # Safety: stop if consecutive failures
            if step_num >= 3:
                last_3 = context.steps[-3:]
                if all(not s.success for s in last_3):
                    logger.error(f"3 consecutive failures — stopping agent")
                    final_answer = "Unable to complete task: repeated tool failures. Please check tool configuration."
                    break
        else:
            # Exhausted max steps — summarize what was found
            notes_result = await self.tools.execute("read_notes", {})
            final_answer = f"Reached step limit ({max_steps}). Research notes:\n\n{notes_result.output}"

        # ── Post-task: Store outcome + extract lessons ────────────────────
        quality = self._estimate_quality(context)
        failure_pattern = self._detect_failure_pattern(context)

        asyncio.create_task(
            self.trace_collector.store_outcome(
                context=context,
                final_answer=final_answer,
                quality_score=quality,
                failure_pattern=failure_pattern,
                task_category=task_category,
            )
        )

        # Extract and store failure lesson if quality was low
        if quality < 0.65 and failure_pattern:
            asyncio.create_task(
                self.failure_memory.extract_and_store_lesson(
                    task=task,
                    context=context,
                    failure_pattern=failure_pattern,
                    quality_score=quality,
                )
            )

        # Update capability map
        asyncio.create_task(
            self.capability_map.update(
                task_category=task_category,
                quality_score=quality,
                steps_taken=len(context.steps),
                failure_pattern=failure_pattern,
            )
        )

        if stream_callback:
            await stream_callback("agent_done", {
                "quality_score": quality,
                "total_steps": len(context.steps),
                "failure_pattern": failure_pattern,
                "task_category": task_category,
            })

        return AgentResult(
            context=context,
            final_answer=final_answer,
            total_steps=len(context.steps),
            success=quality > 0.5,
            quality_score=quality,
            failure_pattern=failure_pattern,
        )

    def _estimate_quality(self, context: AgentContext) -> float:
        """Heuristic quality score from step data. Not perfect — that's fine."""
        if not context.steps:
            return 0.0
        success_rate = sum(1 for s in context.steps if s.success) / len(context.steps)
        has_notes = any(s.thought.action == "write_note" for s in context.steps)
        has_finish = any(s.thought.action == "finish" for s in context.steps)
        used_multiple_tools = len({s.thought.action for s in context.steps}) > 2

        score = success_rate * 0.5
        if has_notes: score += 0.15
        if has_finish: score += 0.25
        if used_multiple_tools: score += 0.10
        return min(score, 1.0)

    def _detect_failure_pattern(self, context: AgentContext) -> str | None:
        if not context.steps:
            return None
        actions = [s.thought.action for s in context.steps]
        failures = [s for s in context.steps if not s.success]

        if len(failures) / max(len(context.steps), 1) > 0.4:
            return "tool_failure"
        if actions.count("web_search") > 4:
            return "tool_overuse"
        if not any(a == "finish" for a in actions):
            return "goal_drift"
        if actions.count(actions[0]) > 3:
            return "stuck_loop"
        return None
EOF
```

✅ **VERIFY:**
```bash
uv run python -c "
from backend.agent.agent_loop import AgentRunner
print('AgentRunner imported OK')
from backend.agent.goal_anchor import GoalAnchor
anchor = GoalAnchor('test task about machine learning')
sig = anchor.check(3, 'thinking about machine learning algorithms and models')
print('Drift check OK, drifted:', sig.drifted, 'score:', round(sig.drift_score, 3))
"
```

---

## STEP 4 — OBSERVABILITY LAYER (Layer 1 + 2)

### 4.1 — Trace Collector

```bash
mkdir -p backend/agent/observability
touch backend/agent/observability/__init__.py

cat > backend/agent/observability/trace_collector.py << 'EOF'
"""
Stores every agent step as a searchable vector in Postgres.
The agent can query its OWN past behavior semantically —
the same infra as RAG retrieval, pointed at agent memory.
"""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from loguru import logger

from backend.app.agent_models import AgentTrace, TaskOutcome
from backend.agent.context import AgentContext, StepRecord
from backend.rag_engine.embeddings import embed_query


class TraceCollector:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def store_trace(
        self,
        context: AgentContext,
        step: StepRecord,
        step_score: float = 0.5,
        eval_note: str = "",
    ) -> None:
        # Embed the combined trace for self-search
        trace_text = (
            f"Task: {context.task[:200]} | "
            f"Action: {step.thought.action} | "
            f"Reasoning: {step.thought.reasoning[:300]} | "
            f"Result: {step.result_output[:300]}"
        )
        embedding = embed_query(trace_text)

        trace = AgentTrace(
            session_id=context.session_id,
            task_id=context.task_id,
            step_number=step.step_num,
            action=step.thought.action,
            action_args=step.thought.args,
            result=step.result_output[:2000],
            result_summary=step.result_output[:400],
            reasoning=step.thought.reasoning,
            confidence=step.thought.confidence,
            model_used=context.model_override or "default",
            latency_ms=step.latency_ms,
            token_count=step.token_count,
            success=step.success,
            step_score=step_score,
            embedding=embedding,
        )
        self.db.add(trace)
        try:
            await self.db.commit()
        except Exception as e:
            logger.error(f"Trace store error: {e}")
            await self.db.rollback()

    async def store_outcome(
        self,
        context: AgentContext,
        final_answer: str,
        quality_score: float,
        failure_pattern: str | None,
        task_category: str,
    ) -> None:
        embedding = embed_query(context.task)
        outcome = TaskOutcome(
            session_id=context.session_id,
            task_description=context.task,
            task_category=task_category,
            total_steps=len(context.steps),
            final_success=quality_score > 0.5,
            quality_score=quality_score,
            dominant_failure=failure_pattern,
            model_used=context.model_override or "default",
            focus_mode=context.focus_mode,
            embedding=embedding,
            traces_json=[str(s.step_num) for s in context.steps],
        )
        self.db.add(outcome)
        try:
            await self.db.commit()
        except Exception as e:
            logger.error(f"Outcome store error: {e}")
            await self.db.rollback()

    async def query_similar_past_runs(
        self,
        current_task: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Agent queries its own past behavior — 'Have I done something like this before?'"""
        embedding = embed_query(current_task)
        rows = await self.db.execute(text("""
            SELECT task_description, task_category, total_steps,
                   final_success, quality_score, dominant_failure,
                   1 - (embedding <=> :vec::vector) AS similarity
            FROM task_outcomes
            ORDER BY embedding <=> :vec::vector
            LIMIT :k
        """), {"vec": str(embedding), "k": top_k})

        return [dict(r._mapping) for r in rows.fetchall()]

    async def get_session_traces(self, session_id: str) -> list[dict]:
        rows = await self.db.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .order_by(AgentTrace.step_number)
        )
        traces = rows.scalars().all()
        return [
            {
                "step": t.step_number,
                "action": t.action,
                "reasoning": t.reasoning,
                "result_summary": t.result_summary,
                "success": t.success,
                "step_score": t.step_score,
                "latency_ms": t.latency_ms,
            }
            for t in traces
        ]
EOF
```

### 4.2 — Failure Memory (Layer 3)

```bash
cat > backend/agent/observability/failure_memory.py << 'EOF'
"""
Stores and retrieves structured failure lessons.
Injected into agent system prompt before each task — persistent cross-session learning.
Lessons validated/decayed based on whether they actually helped.
"""
import re
import json
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from loguru import logger

from backend.app.agent_models import FailureLesson
from backend.agent.context import AgentContext
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()

LESSON_EXTRACTION_PROMPT = """You are analyzing a failed AI research agent run to extract a reusable lesson.

Task: {task}
Task Category: {task_category}
Total Steps: {total_steps}
Failure Pattern: {failure_pattern}
Quality Score: {quality_score:.2f}

Step History:
{step_history}

Extract a structured lesson for future runs. Output ONLY valid JSON:
{{
  "situation_type": "brief category name e.g. multi-hop research",
  "trigger_pattern": "the specific pattern that triggered this failure e.g. query asks to compare X and Y",
  "what_failed": "concrete description of what went wrong",
  "why_it_failed": "root cause analysis",
  "better_approach": "step-by-step better strategy for next time",
  "example_task": "the original task as reference"
}}"""


class FailureMemory:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_relevant_lessons(self, task: str, top_k: int = 3) -> str:
        """Retrieve relevant past failure lessons before starting a task."""
        embedding = embed_query(task)

        rows = await self.db.execute(text("""
            SELECT situation_type, trigger_pattern, better_approach,
                   confidence, validated_count, failed_count,
                   1 - (embedding <=> :vec::vector) AS similarity
            FROM failure_lessons
            WHERE confidence > 0.3
            ORDER BY embedding <=> :vec::vector
            LIMIT :k
        """), {"vec": str(embedding), "k": top_k})

        lessons = rows.fetchall()
        if not lessons:
            return ""

        lines = ["LESSONS FROM PAST FAILURES:"]
        for lesson in lessons:
            reliability = lesson.validated_count / max(lesson.validated_count + lesson.failed_count, 1)
            if lesson.similarity < 0.5:
                continue  # too dissimilar — skip
            lines.append(
                f"Pattern: {lesson.trigger_pattern}\n"
                f"Avoid: {lesson.what_failed if hasattr(lesson, 'what_failed') else ''}\n"
                f"Better approach: {lesson.better_approach}\n"
                f"Reliability: {reliability:.0%} ({lesson.validated_count} validations)"
            )
        return "\n\n".join(lines) if len(lines) > 1 else ""

    async def extract_and_store_lesson(
        self,
        task: str,
        context: AgentContext,
        failure_pattern: str,
        quality_score: float,
    ) -> None:
        """Use LLM to extract a structured lesson from this failure."""
        step_history = context.to_prompt_history(max_steps=8)

        from backend.agent.observability.task_classifier import classify_task
        task_category = await classify_task(task)

        prompt = LESSON_EXTRACTION_PROMPT.format(
            task=task,
            task_category=task_category,
            total_steps=len(context.steps),
            failure_pattern=failure_pattern,
            quality_score=quality_score,
            step_history=step_history[:1500],
        )

        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=settings.smart_model,  # phi4-mini — needs reasoning
            prompt=prompt,
            options={"temperature": 0.2, "num_predict": 400},
        )
        raw = resp["response"].strip()
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning("Failed to extract lesson — no JSON in response")
            return

        try:
            data = json.loads(match.group())
        except json.JSONDecodeError as e:
            logger.error(f"Lesson JSON parse failed: {e}")
            return

        trigger_text = data.get("trigger_pattern", task[:200])
        embedding = embed_query(trigger_text)

        lesson = FailureLesson(
            situation_type=data.get("situation_type", failure_pattern),
            trigger_pattern=data.get("trigger_pattern", ""),
            what_failed=data.get("what_failed", ""),
            why_it_failed=data.get("why_it_failed", ""),
            better_approach=data.get("better_approach", ""),
            example_task=data.get("example_task", task[:400]),
            confidence=0.5,
            embedding=embedding,
        )
        self.db.add(lesson)
        try:
            await self.db.commit()
            logger.info(f"Stored failure lesson: {lesson.situation_type}")
        except Exception as e:
            logger.error(f"Failed to store lesson: {e}")
            await self.db.rollback()

    async def validate_lesson(self, lesson_id: str) -> None:
        """Call when a lesson was retrieved and the task succeeded."""
        from sqlalchemy import select
        import uuid
        lesson = await self.db.get(FailureLesson, uuid.UUID(lesson_id))
        if lesson:
            lesson.validated_count += 1
            lesson.confidence = lesson.reliability_score
            await self.db.commit()

    async def decay_lesson(self, lesson_id: str) -> None:
        """Call when a lesson was retrieved but task still failed."""
        from sqlalchemy import select
        import uuid
        lesson = await self.db.get(FailureLesson, uuid.UUID(lesson_id))
        if lesson:
            lesson.failed_count += 1
            lesson.confidence = lesson.reliability_score
            if lesson.confidence < 0.1:
                await self.db.delete(lesson)  # prune consistently wrong lessons
            await self.db.commit()
EOF
```

### 4.3 — Task Classifier

```bash
cat > backend/agent/observability/task_classifier.py << 'EOF'
"""
Classifies incoming tasks into categories for the capability map.
Uses fast keyword matching first, LLM fallback for ambiguous cases.
"""
import re
import ollama
from backend.app.config import get_settings

settings = get_settings()

TASK_CATEGORIES = [
    "single_fact_lookup",
    "multi_hop_research",
    "comparative_analysis",
    "paper_summarization",
    "hypothesis_generation",
    "code_explanation",
    "long_context_synthesis",
    "ambiguous_query",
]

# Fast keyword rules — avoids LLM call for obvious cases
KEYWORD_RULES = {
    "single_fact_lookup":    [r"\bwhat is\b", r"\bwho is\b", r"\bwhen did\b", r"\bdefine\b"],
    "comparative_analysis":  [r"\bcompare\b", r"\bvs\b", r"\bdifference between\b", r"\bwhich is better\b"],
    "paper_summarization":   [r"\bsummariz\b", r"\bexplain.*paper\b", r"\bwhat does.*paper\b"],
    "code_explanation":      [r"\bcode\b", r"\bfunction\b", r"\bimpleme\b", r"\bpython\b", r"\bjavascript\b"],
    "hypothesis_generation": [r"\bhypothe\b", r"\bwhat if\b", r"\bcould\b.*\bhappen\b"],
}

CLASSIFY_PROMPT = """Classify this research task into ONE category:
- single_fact_lookup: looking up a single fact
- multi_hop_research: needs multiple searches to answer
- comparative_analysis: comparing multiple things
- paper_summarization: summarizing a paper
- hypothesis_generation: generating new ideas or hypotheses
- code_explanation: explaining or debugging code
- long_context_synthesis: synthesizing many sources
- ambiguous_query: unclear or broad

Task: {task}

Output ONLY the category name, nothing else."""


async def classify_task(task: str) -> str:
    task_lower = task.lower()

    # Fast path: keyword matching
    for category, patterns in KEYWORD_RULES.items():
        for pattern in patterns:
            if re.search(pattern, task_lower):
                return category

    # Slow path: LLM classification
    try:
        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=settings.fast_model,  # llama3.2 — fast, just classification
            prompt=CLASSIFY_PROMPT.format(task=task),
            options={"temperature": 0.0, "num_predict": 20},
        )
        category = resp["response"].strip().lower().replace(" ", "_")
        if category in TASK_CATEGORIES:
            return category
    except Exception:
        pass

    return "ambiguous_query"
EOF
```

### 4.4 — Capability Map (Layer 5a)

```bash
cat > backend/agent/observability/capability_map.py << 'EOF'
"""
Tracks agent success rates by task category.
Provides hints to the planner about known weak areas.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from backend.app.agent_models import CapabilityRecord
from backend.agent.observability.task_classifier import TASK_CATEGORIES


class CapabilityMap:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update(
        self,
        task_category: str,
        quality_score: float,
        steps_taken: int,
        failure_pattern: str | None,
    ) -> None:
        result = await self.db.execute(
            select(CapabilityRecord).where(CapabilityRecord.task_category == task_category)
        )
        record = result.scalar_one_or_none()

        if not record:
            record = CapabilityRecord(task_category=task_category)
            self.db.add(record)

        n = record.total_attempts
        record.total_attempts += 1
        if quality_score > 0.5:
            record.success_count += 1
        # Running average
        record.avg_quality = (record.avg_quality * n + quality_score) / (n + 1)
        record.avg_steps = (record.avg_steps * n + steps_taken) / (n + 1)
        if failure_pattern:
            record.most_common_failure = failure_pattern

        try:
            await self.db.commit()
        except Exception as e:
            logger.error(f"CapabilityMap update error: {e}")
            await self.db.rollback()

    async def get_hints_for_task(self, task_category: str) -> str:
        result = await self.db.execute(
            select(CapabilityRecord).where(CapabilityRecord.task_category == task_category)
        )
        record = result.scalar_one_or_none()

        if not record or record.total_attempts < 2:
            return ""

        if record.is_weak:
            hint = (
                f"⚠️ CAPABILITY WARNING: You have historically struggled with "
                f"'{task_category}' tasks (avg quality: {record.avg_quality:.0%}, "
                f"success rate: {record.success_rate:.0%} over {record.total_attempts} attempts).\n"
            )
            if record.most_common_failure:
                hint += f"Most common failure pattern: '{record.most_common_failure}'.\n"
            hint += "Consider: use write_note to accumulate findings before synthesizing. Be more systematic."
            return hint
        return ""

    async def get_full_map(self) -> list[dict]:
        result = await self.db.execute(select(CapabilityRecord))
        records = result.scalars().all()
        return [
            {
                "category": r.task_category,
                "attempts": r.total_attempts,
                "success_rate": round(r.success_rate, 3),
                "avg_quality": round(r.avg_quality, 3),
                "avg_steps": round(r.avg_steps, 1),
                "is_weak": r.is_weak,
                "common_failure": r.most_common_failure,
            }
            for r in sorted(records, key=lambda x: x.avg_quality)
        ]

    async def get_weak_areas(self) -> list[str]:
        full = await self.get_full_map()
        return [r["category"] for r in full if r["is_weak"]]
EOF
```

✅ **VERIFY:**
```bash
uv run python -c "
import asyncio
from backend.agent.observability.task_classifier import classify_task

async def test():
    tests = [
        ('What is RAG?', 'single_fact_lookup'),
        ('Compare BERT and GPT-4', 'comparative_analysis'),
        ('Explain this Python code', 'code_explanation'),
        ('Multi-hop: how does attention relate to transformers and what papers prove it', 'multi_hop_research'),
    ]
    for task, expected in tests:
        result = await classify_task(task)
        status = '✓' if result == expected else f'? (got {result})'
        print(f'{status} {task[:50]}')

asyncio.run(test())
"
```

---

## STEP 5 — STRATEGY LIBRARY (Layer 5b Meta-Learning)

```bash
cat > backend/agent/observability/strategy_library.py << 'EOF'
"""
Learned task-solving playbooks.
Starts empty. Agent generates new strategies after failures.
You approve them (10 seconds). System applies them forever.
"""
import re
import json
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from loguru import logger

from backend.app.agent_models import Strategy
from backend.rag_engine.embeddings import embed_query
from backend.app.config import get_settings

settings = get_settings()

STRATEGY_EVOLUTION_PROMPT = """An AI research agent failed at this type of task.
Failure pattern: {failure_pattern}
Task category: {task_category}
Current approach (if any): {current_strategy}
Example failed task: {example_task}
What went wrong: {what_failed}

Write a concise, actionable step-by-step strategy to handle this task type better.
Be specific. Include: when to use it, what to do at each step, what to avoid.

Output ONLY JSON:
{{
  "trigger_description": "when to apply this strategy",
  "strategy_text": "1. First do X\\n2. Then Y\\n3. Finally Z",
  "expected_improvement": "brief explanation of why this is better"
}}"""


class StrategyLibrary:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_relevant_strategy(self, task: str) -> str | None:
        embedding = embed_query(task)
        rows = await self.db.execute(text("""
            SELECT trigger_description, strategy_text, success_rate, sample_size
            FROM strategy_library
            WHERE approved = true AND success_rate > 0.55
            ORDER BY embedding <=> :vec::vector
            LIMIT 1
        """), {"vec": str(embedding)})
        row = rows.fetchone()
        if row and row.success_rate > 0.55 and row.sample_size >= 2:
            return (
                f"LEARNED STRATEGY (success rate: {row.success_rate:.0%}, "
                f"n={row.sample_size}):\n{row.strategy_text}"
            )
        return None

    async def evolve_strategy(
        self,
        task_category: str,
        failure_pattern: str,
        example_task: str,
        what_failed: str,
    ) -> str | None:
        """Generate a new strategy after a failure. Returns strategy ID for approval."""
        # Check if we have an existing strategy for this category
        rows = await self.db.execute(text("""
            SELECT strategy_text FROM strategy_library
            WHERE trigger_description ILIKE :cat
            LIMIT 1
        """), {"cat": f"%{task_category}%"})
        existing_row = rows.fetchone()
        current_strategy = existing_row.strategy_text if existing_row else "No existing strategy"

        prompt = STRATEGY_EVOLUTION_PROMPT.format(
            failure_pattern=failure_pattern,
            task_category=task_category,
            current_strategy=current_strategy[:500],
            example_task=example_task[:300],
            what_failed=what_failed[:300],
        )

        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=settings.smart_model,
            prompt=prompt,
            options={"temperature": 0.3, "num_predict": 400},
        )
        raw = resp["response"].strip()
        raw = re.sub(r"```json\s*|\s*```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None

        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None

        trigger = data.get("trigger_description", task_category)
        embedding = embed_query(trigger)

        strategy = Strategy(
            trigger_description=trigger,
            strategy_text=data.get("strategy_text", ""),
            source="agent",
            success_rate=0.5,
            sample_size=1,
            approved=False,  # REQUIRES HUMAN APPROVAL
            embedding=embedding,
        )
        self.db.add(strategy)
        await self.db.commit()

        logger.info(f"New strategy proposed (pending approval): {trigger[:60]}")
        return str(strategy.id)

    async def get_pending_approvals(self) -> list[dict]:
        """Returns strategies awaiting human approval."""
        result = await self.db.execute(
            select(Strategy).where(Strategy.approved == False)  # noqa: E712
            .order_by(Strategy.created_at.desc())
        )
        strategies = result.scalars().all()
        return [
            {
                "id": str(s.id),
                "trigger": s.trigger_description,
                "strategy": s.strategy_text,
                "source": s.source,
                "created_at": s.created_at.isoformat(),
            }
            for s in strategies
        ]

    async def approve_strategy(self, strategy_id: str) -> bool:
        import uuid
        strategy = await self.db.get(Strategy, uuid.UUID(strategy_id))
        if not strategy:
            return False
        strategy.approved = True
        await self.db.commit()
        logger.info(f"Strategy approved: {strategy.trigger_description[:60]}")
        return True

    async def update_strategy_performance(self, strategy_id: str, succeeded: bool) -> None:
        import uuid
        strategy = await self.db.get(Strategy, uuid.UUID(strategy_id))
        if not strategy:
            return
        n = strategy.sample_size
        strategy.sample_size += 1
        strategy.success_rate = (strategy.success_rate * n + (1.0 if succeeded else 0.0)) / (n + 1)
        # Auto-retire strategies with consistently poor performance
        if strategy.sample_size >= 5 and strategy.success_rate < 0.25:
            strategy.approved = False
            logger.warning(f"Auto-retired poor strategy: {strategy.trigger_description[:60]}")
        await self.db.commit()
EOF
```

---

## STEP 6 — AGENT API ROUTES

```bash
cat > backend/app/routes/agent.py << 'EOF'
"""
Agent API endpoints.
/agent/run     → start a research task (SSE stream)
/agent/traces  → get step-by-step trace for a session
/agent/capability-map → see agent's self-knowledge
/agent/strategies/pending → human approval queue
/agent/strategies/{id}/approve → approve a strategy
/agent/corrections → log a human correction (digital twin data)
"""
import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_session
from backend.agent.agent_loop import AgentRunner
from backend.agent.observability.capability_map import CapabilityMap
from backend.agent.observability.strategy_library import StrategyLibrary
from backend.agent.observability.trace_collector import TraceCollector
from backend.app.agent_models import UserCorrection
from backend.rag_engine.embeddings import embed_query

router = APIRouter()


class AgentRunRequest(BaseModel):
    task: str = Field(..., min_length=5, max_length=3000)
    session_id: str = Field(...)
    focus_mode: str = Field(default="research")
    model: str | None = None
    max_steps: int = Field(default=10, ge=3, le=20)


class CorrectionRequest(BaseModel):
    task_id: str
    situation: str
    agent_approach: str
    your_approach: str
    reason: str | None = None
    domain: str = "general"


class StrategyApprovalRequest(BaseModel):
    strategy_id: str


async def _agent_sse_stream(
    runner: AgentRunner,
    req: AgentRunRequest,
) -> AsyncGenerator[str, None]:
    """Wraps AgentRunner.run() as SSE events for the frontend."""
    queue: asyncio.Queue = asyncio.Queue()

    async def callback(event_type: str, data: dict):
        await queue.put((event_type, data))

    async def run_agent():
        try:
            result = await runner.run(
                task=req.task,
                session_id=req.session_id,
                focus_mode=req.focus_mode,
                model_override=req.model,
                max_steps=req.max_steps,
                stream_callback=callback,
            )
            await queue.put(("final_answer", {
                "answer": result.final_answer,
                "quality": result.quality_score,
                "total_steps": result.total_steps,
                "failure_pattern": result.failure_pattern,
            }))
        except Exception as e:
            await queue.put(("error", {"message": str(e)}))
        finally:
            await queue.put(None)  # sentinel

    task = asyncio.create_task(run_agent())

    while True:
        item = await queue.get()
        if item is None:
            break
        event_type, data = item
        yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    await task


@router.post("/run")
async def run_agent(
    req: AgentRunRequest,
    db: AsyncSession = Depends(get_session),
):
    runner = AgentRunner(db)
    return StreamingResponse(
        _agent_sse_stream(runner, req),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/traces/{session_id}")
async def get_traces(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    collector = TraceCollector(db)
    traces = await collector.get_session_traces(session_id)
    return {"session_id": session_id, "traces": traces}


@router.get("/similar-past-runs")
async def get_similar_past_runs(
    task: str,
    db: AsyncSession = Depends(get_session),
):
    collector = TraceCollector(db)
    similar = await collector.query_similar_past_runs(task, top_k=5)
    return {"similar_runs": similar}


@router.get("/capability-map")
async def get_capability_map(db: AsyncSession = Depends(get_session)):
    cap_map = CapabilityMap(db)
    full = await cap_map.get_full_map()
    weak = await cap_map.get_weak_areas()
    return {"capability_map": full, "weak_areas": weak}


@router.get("/strategies/pending")
async def get_pending_strategies(db: AsyncSession = Depends(get_session)):
    library = StrategyLibrary(db)
    pending = await library.get_pending_approvals()
    return {"pending": pending, "count": len(pending)}


@router.post("/strategies/{strategy_id}/approve")
async def approve_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_session),
):
    library = StrategyLibrary(db)
    ok = await library.approve_strategy(strategy_id)
    if not ok:
        raise HTTPException(404, "Strategy not found")
    return {"approved": True, "strategy_id": strategy_id}


@router.post("/corrections")
async def log_correction(
    req: CorrectionRequest,
    db: AsyncSession = Depends(get_session),
):
    """Log human corrections — training data for digital twin."""
    text = f"{req.situation} | agent: {req.agent_approach} | better: {req.your_approach}"
    embedding = embed_query(text)

    correction = UserCorrection(
        task_id=req.task_id,
        situation=req.situation,
        agent_approach=req.agent_approach,
        your_approach=req.your_approach,
        reason=req.reason,
        domain=req.domain,
        embedding=embedding,
    )
    db.add(correction)
    await db.commit()
    return {"logged": True, "correction_id": str(correction.id)}
EOF
```

### Register Agent Router in main.py

```bash
# Add to backend/app/main.py imports and router registration
cat >> backend/app/main.py << 'EOF'

# Add this import at top of file:
# from backend.app.routes import agent as agent_route

# Add this line with the other app.include_router calls:
# app.include_router(agent_route.router, prefix="/agent", tags=["agent"])
EOF

# Actually do the edit properly:
sed -i 's/from backend.app.routes import search, documents, health, history, models, feedback/from backend.app.routes import search, documents, health, history, models, feedback, agent as agent_route/' backend/app/main.py
sed -i 's/app.include_router(feedback.router,  prefix="\/feedback",  tags=\["feedback"\])/app.include_router(feedback.router,  prefix="\/feedback",  tags=["feedback"])\napp.include_router(agent_route.router, prefix="\/agent",     tags=["agent"])/' backend/app/main.py
```

✅ **VERIFY:**
```bash
docker compose up --build -d
sleep 8
curl http://localhost:8000/health | python3 -m json.tool
curl http://localhost:8000/agent/capability-map | python3 -m json.tool
# Should return: {"capability_map": [], "weak_areas": []}
```

---

## STEP 7 — DAILY EVOLUTION PROTOCOL (Phase 4)

```bash
cat > backend/agent/digital_twin/evolution_protocol.py << 'EOF'
"""
Daily Evolution Protocol — runs every 24 hours.
Reviews yesterday's traces, proposes strategy updates, queues for human approval.
This is the human-in-loop RSI mechanism.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from backend.app.agent_models import TaskOutcome, FailureLesson, CapabilityRecord
from backend.agent.observability.strategy_library import StrategyLibrary
from backend.app.config import get_settings

settings = get_settings()


class DailyEvolutionReport:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_daily_report(self) -> dict:
        """Summarize yesterday's runs and propose improvements."""
        yesterday = datetime.utcnow() - timedelta(hours=24)

        # Get yesterday's outcomes
        result = await self.db.execute(
            select(TaskOutcome).where(TaskOutcome.created_at >= yesterday)
        )
        outcomes = result.scalars().all()

        if not outcomes:
            return {"message": "No agent runs in the last 24 hours.", "proposals": []}

        total = len(outcomes)
        succeeded = sum(1 for o in outcomes if o.final_success)
        avg_quality = sum(o.quality_score or 0 for o in outcomes) / total
        avg_steps = sum(o.total_steps for o in outcomes) / total

        # Find top failure patterns
        failure_counts: dict[str, int] = {}
        for o in outcomes:
            if o.dominant_failure:
                failure_counts[o.dominant_failure] = failure_counts.get(o.dominant_failure, 0) + 1
        top_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # Get weak categories
        cap_result = await self.db.execute(
            select(CapabilityRecord).where(CapabilityRecord.total_attempts >= 3)
        )
        cap_records = cap_result.scalars().all()
        weak_categories = [r.task_category for r in cap_records if r.is_weak]

        # Generate strategy proposals for each top failure
        proposals = []
        library = StrategyLibrary(self.db)

        for failure_pattern, count in top_failures[:2]:
            # Find a recent example of this failure
            example_outcome = next(
                (o for o in outcomes if o.dominant_failure == failure_pattern), None
            )
            if example_outcome:
                strategy_id = await library.evolve_strategy(
                    task_category=example_outcome.task_category,
                    failure_pattern=failure_pattern,
                    example_task=example_outcome.task_description[:300],
                    what_failed=f"Failure pattern: {failure_pattern}",
                )
                if strategy_id:
                    proposals.append({
                        "strategy_id": strategy_id,
                        "failure_pattern": failure_pattern,
                        "occurrences": count,
                    })

        report = {
            "period": "last_24_hours",
            "stats": {
                "total_tasks": total,
                "succeeded": succeeded,
                "failed": total - succeeded,
                "success_rate": round(succeeded / total, 3),
                "avg_quality": round(avg_quality, 3),
                "avg_steps": round(avg_steps, 1),
            },
            "top_failures": [{"pattern": f, "count": c} for f, c in top_failures],
            "weak_categories": weak_categories,
            "proposals": proposals,
            "action_required": len(proposals) > 0,
        }

        logger.info(
            f"Daily report: {total} tasks, {succeeded} succeeded, "
            f"{len(proposals)} strategy proposals pending approval"
        )
        return report


async def run_daily_evolution(db: AsyncSession) -> dict:
    """Entry point for scheduled daily evolution."""
    protocol = DailyEvolutionReport(db)
    return await protocol.generate_daily_report()
EOF

mkdir -p backend/agent/digital_twin
touch backend/agent/digital_twin/__init__.py
```

### Daily Evolution API Endpoint

```bash
cat >> backend/app/routes/agent.py << 'EOF'


@router.get("/daily-report")
async def get_daily_report(db: AsyncSession = Depends(get_session)):
    """Generate the daily evolution report — call this every morning."""
    from backend.agent.digital_twin.evolution_protocol import run_daily_evolution
    report = await run_daily_evolution(db)
    return report
EOF
```

---

## STEP 8 — FRONTEND: AGENT TRACE VISUALIZATION

### 8.1 — Agent Trace Panel Component

```bash
cat > frontend/src/components/AgentTracePanel.tsx << 'EOF'
"use client";
/**
 * Real-time agent trace visualization — shows the agent's thinking step by step.
 * Perplexity-style but for the agent: each step shows action, reasoning, result.
 */
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Search, BookOpen, FileText, CheckCircle, XCircle, Loader2, ChevronDown } from "lucide-react";

export interface AgentStep {
  step: number;
  action: string;
  reasoning: string;
  result_preview: string;
  success: boolean;
  step_score: number;
  latency_ms: number;
}

interface AgentTracePanelProps {
  steps: AgentStep[];
  isRunning: boolean;
  currentAction?: string;
  qualityScore?: number;
  totalSteps?: number;
  driftDetected?: boolean;
}

const ACTION_ICONS: Record<string, React.ReactNode> = {
  "search_knowledge_base": <BookOpen className="w-3.5 h-3.5" />,
  "web_search":            <Search className="w-3.5 h-3.5" />,
  "arxiv_search":          <FileText className="w-3.5 h-3.5" />,
  "wikipedia_search":      <FileText className="w-3.5 h-3.5" />,
  "write_note":            <Brain className="w-3.5 h-3.5" />,
  "read_notes":            <Brain className="w-3.5 h-3.5" />,
  "finish":                <CheckCircle className="w-3.5 h-3.5" />,
};

const ACTION_COLORS: Record<string, string> = {
  "search_knowledge_base": "text-purple-400",
  "web_search":            "text-blue-400",
  "arxiv_search":          "text-amber-400",
  "wikipedia_search":      "text-green-400",
  "write_note":            "text-plex-accent",
  "finish":                "text-green-400",
};

function ScoreBar({ score }: { score: number }) {
  const color = score >= 0.7 ? "bg-green-500" : score >= 0.45 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-plex-border rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${score * 100}%` }} />
      </div>
      <span className="text-[10px] text-plex-muted">{(score * 100).toFixed(0)}%</span>
    </div>
  );
}

function StepCard({ step, index }: { step: AgentStep; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const actionColor = ACTION_COLORS[step.action] || "text-plex-muted";
  const icon = ACTION_ICONS[step.action] || <Brain className="w-3.5 h-3.5" />;

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="border border-plex-border rounded-xl overflow-hidden"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-3 bg-plex-surface hover:bg-plex-hover transition-colors text-left"
      >
        <span className="text-xs text-plex-muted w-5 shrink-0 font-mono">{step.step}</span>

        <span className={`shrink-0 ${actionColor}`}>{icon}</span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-xs font-mono font-medium ${actionColor}`}>{step.action}</span>
            <ScoreBar score={step.step_score} />
          </div>
          <p className="text-xs text-plex-muted line-clamp-1 mt-0.5">{step.reasoning}</p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {step.success
            ? <CheckCircle className="w-3.5 h-3.5 text-green-500" />
            : <XCircle className="w-3.5 h-3.5 text-red-500" />
          }
          <span className="text-[10px] text-plex-subtle">{step.latency_ms.toFixed(0)}ms</span>
          <ChevronDown className={`w-3.5 h-3.5 text-plex-muted transition-transform ${expanded ? "rotate-180" : ""}`} />
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: "auto" }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 bg-plex-bg border-t border-plex-border">
              <p className="text-xs text-plex-muted mt-2 mb-1 font-semibold">REASONING</p>
              <p className="text-xs text-plex-text font-mono">{step.reasoning}</p>
              <p className="text-xs text-plex-muted mt-2 mb-1 font-semibold">RESULT</p>
              <p className="text-xs text-plex-text font-mono whitespace-pre-wrap">{step.result_preview}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function AgentTracePanel({
  steps, isRunning, currentAction, qualityScore, totalSteps, driftDetected
}: AgentTracePanelProps) {
  if (!steps.length && !isRunning) return null;

  return (
    <div className="mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-plex-muted uppercase tracking-wider flex items-center gap-2">
          <Brain className="w-3.5 h-3.5 text-plex-accent" />
          Agent Reasoning
          {isRunning && <Loader2 className="w-3 h-3 animate-spin text-plex-accent" />}
        </h3>
        {qualityScore !== undefined && !isRunning && (
          <div className="flex items-center gap-2">
            <ScoreBar score={qualityScore} />
            <span className="text-xs text-plex-muted">{totalSteps} steps</span>
          </div>
        )}
      </div>

      {/* Drift warning */}
      {driftDetected && (
        <div className="mb-3 p-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-xs text-amber-400">
          ⚠️ Goal drift detected — agent self-correcting
        </div>
      )}

      {/* Current action (streaming) */}
      {isRunning && currentAction && (
        <div className="flex items-center gap-2 p-3 bg-plex-surface rounded-xl border border-plex-accent/30 mb-2 animate-pulse">
          <Loader2 className="w-3.5 h-3.5 text-plex-accent animate-spin" />
          <span className="text-xs text-plex-accent font-mono">{currentAction}</span>
        </div>
      )}

      {/* Steps */}
      <div className="space-y-2">
        {steps.map((step, i) => (
          <StepCard key={step.step} step={step} index={i} />
        ))}
      </div>
    </div>
  );
}
EOF
```

### 8.2 — Capability Dashboard Component

```bash
cat > frontend/src/components/CapabilityDashboard.tsx << 'EOF'
"use client";
import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle2 } from "lucide-react";

interface CapabilityRecord {
  category: string;
  attempts: number;
  success_rate: number;
  avg_quality: number;
  avg_steps: number;
  is_weak: boolean;
  common_failure: string | null;
}

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function CapabilityDashboard() {
  const [data, setData] = useState<CapabilityRecord[]>([]);
  const [weakAreas, setWeakAreas] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/agent/capability-map`)
      .then(r => r.json())
      .then(d => {
        setData(d.capability_map || []);
        setWeakAreas(d.weak_areas || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse h-32 bg-plex-surface rounded-xl" />;
  if (!data.length) return (
    <div className="text-center py-8 text-plex-muted text-sm">
      No capability data yet. Run some agent tasks first.
    </div>
  );

  const getQualityColor = (q: number) =>
    q >= 0.7 ? "text-green-400" : q >= 0.5 ? "text-amber-400" : "text-red-400";

  const QualityIcon = ({ q }: { q: number }) =>
    q >= 0.7 ? <TrendingUp className="w-3.5 h-3.5 text-green-400" /> :
    q >= 0.5 ? <Minus className="w-3.5 h-3.5 text-amber-400" /> :
    <TrendingDown className="w-3.5 h-3.5 text-red-400" />;

  return (
    <div>
      <h3 className="text-sm font-semibold text-plex-text mb-4 flex items-center gap-2">
        Agent Capability Map
        {weakAreas.length > 0 && (
          <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">
            {weakAreas.length} weak area{weakAreas.length > 1 ? "s" : ""}
          </span>
        )}
      </h3>

      <div className="space-y-2">
        {data.map(rec => (
          <div
            key={rec.category}
            className={`p-3 rounded-xl border ${rec.is_weak
              ? "bg-red-500/5 border-red-500/20"
              : "bg-plex-surface border-plex-border"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                {rec.is_weak
                  ? <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  : <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
                }
                <span className="text-xs font-medium text-plex-text">
                  {rec.category.replace(/_/g, " ")}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <QualityIcon q={rec.avg_quality} />
                <span className={`text-xs font-bold ${getQualityColor(rec.avg_quality)}`}>
                  {(rec.avg_quality * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-1">
              <div className="w-full h-1.5 bg-plex-border rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${rec.is_weak ? "bg-red-500" : "bg-green-500"}`}
                  style={{ width: `${rec.avg_quality * 100}%` }}
                />
              </div>
              <span className="text-[10px] text-plex-muted whitespace-nowrap">
                {rec.attempts} runs · {rec.avg_steps.toFixed(1)} avg steps
              </span>
            </div>

            {rec.is_weak && rec.common_failure && (
              <p className="text-[10px] text-amber-400 mt-1">
                Common failure: {rec.common_failure.replace(/_/g, " ")}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
EOF
```

### 8.3 — Strategy Approval Panel

```bash
cat > frontend/src/components/StrategyApprovalPanel.tsx << 'EOF'
"use client";
import { useEffect, useState } from "react";
import { Check, X, Lightbulb } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface PendingStrategy {
  id: string;
  trigger: string;
  strategy: string;
  source: string;
  created_at: string;
}

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function StrategyApprovalPanel() {
  const [pending, setPending] = useState<PendingStrategy[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPending = () => {
    fetch(`${API}/agent/strategies/pending`)
      .then(r => r.json())
      .then(d => { setPending(d.pending || []); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(fetchPending, []);

  const approve = async (id: string) => {
    await fetch(`${API}/agent/strategies/${id}/approve`, { method: "POST" });
    setPending(prev => prev.filter(s => s.id !== id));
  };

  const dismiss = (id: string) => {
    setPending(prev => prev.filter(s => s.id !== id));
  };

  if (!pending.length) return null;

  return (
    <div className="mb-6">
      <h3 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-2">
        <Lightbulb className="w-3.5 h-3.5" />
        Strategy Proposals ({pending.length}) — Approve to activate
      </h3>

      <AnimatePresence>
        {pending.map(strategy => (
          <motion.div
            key={strategy.id}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className="mb-3 p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl"
          >
            <p className="text-xs font-medium text-amber-400 mb-1">When: {strategy.trigger}</p>
            <p className="text-xs text-plex-text whitespace-pre-wrap font-mono bg-plex-bg rounded-lg p-2 mb-3">
              {strategy.strategy}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => approve(strategy.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-xs font-medium transition-colors"
              >
                <Check className="w-3.5 h-3.5" /> Approve
              </button>
              <button
                onClick={() => dismiss(strategy.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-xs font-medium transition-colors"
              >
                <X className="w-3.5 h-3.5" /> Dismiss
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
EOF
```

---

## STEP 9 — AGENT MODE PAGE (frontend)

```bash
cat > frontend/src/app/agent/page.tsx << 'EOF'
"use client";
import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Play, Loader2 } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { AgentTracePanel, AgentStep } from "@/components/AgentTracePanel";
import { CapabilityDashboard } from "@/components/CapabilityDashboard";
import { StrategyApprovalPanel } from "@/components/StrategyApprovalPanel";
import { useStore } from "@/lib/store";
import { v4 as uuidv4 } from "uuid";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MAX_STEPS = 10;

export default function AgentPage() {
  const [task, setTask] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [currentAction, setCurrentAction] = useState<string | undefined>();
  const [finalAnswer, setFinalAnswer] = useState<string | null>(null);
  const [qualityScore, setQualityScore] = useState<number | undefined>();
  const [driftDetected, setDriftDetected] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const { sidebarOpen, selectedModel, sessionId } = useStore();

  const handleRun = async () => {
    if (!task.trim() || isRunning) return;
    setIsRunning(true);
    setSteps([]);
    setFinalAnswer(null);
    setQualityScore(undefined);
    setDriftDetected(false);

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    try {
      const res = await fetch(`${API}/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task,
          session_id: sessionId,
          focus_mode: "research",
          model: selectedModel,
          max_steps: MAX_STEPS,
        }),
        signal: abortRef.current.signal,
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let eventType = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6).trim());
            switch (eventType) {
              case "agent_thinking":
                setCurrentAction(data.action);
                break;
              case "agent_step":
                setCurrentAction(undefined);
                setSteps(prev => [...prev, data as AgentStep]);
                break;
              case "drift_detected":
                setDriftDetected(true);
                setTimeout(() => setDriftDetected(false), 5000);
                break;
              case "final_answer":
                setFinalAnswer(data.answer);
                setQualityScore(data.quality);
                setIsRunning(false);
                break;
              case "error":
                setFinalAnswer(`Error: ${data.message}`);
                setIsRunning(false);
                break;
            }
          }
        }
      }
    } catch (e: any) {
      if (e.name !== "AbortError") {
        setFinalAnswer(`Connection error: ${e.message}`);
      }
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-plex-bg flex">
      <Sidebar />
      <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? "ml-64" : "ml-8"}`}>
        <div className="max-w-4xl mx-auto px-6 py-8">

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-plex-text mb-1">Research Agent</h1>
            <p className="text-plex-muted text-sm">
              Multi-step autonomous research with self-improving memory
            </p>
          </div>

          {/* Strategy approvals (if any) */}
          <StrategyApprovalPanel />

          {/* Task input */}
          <div className="mb-6 bg-plex-surface border border-plex-border rounded-2xl p-4">
            <textarea
              value={task}
              onChange={e => setTask(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleRun(); }}
              placeholder="Give the agent a research task... (Ctrl+Enter to run)"
              className="w-full bg-transparent outline-none resize-none text-plex-text placeholder-plex-muted text-sm leading-relaxed"
              rows={3}
            />
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-plex-border">
              <span className="text-xs text-plex-muted">
                Model: {selectedModel} · Max steps: {MAX_STEPS}
              </span>
              <button
                onClick={handleRun}
                disabled={!task.trim() || isRunning}
                className="flex items-center gap-2 px-4 py-2 bg-plex-accent rounded-xl text-black text-sm font-medium hover:bg-opacity-80 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {isRunning ? "Researching..." : "Run Agent"}
              </button>
            </div>
          </div>

          {/* Main content: traces + answer */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AgentTracePanel
                steps={steps}
                isRunning={isRunning}
                currentAction={currentAction}
                qualityScore={qualityScore}
                totalSteps={steps.length}
                driftDetected={driftDetected}
              />

              {finalAnswer && (
                <motion.div
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-plex-surface border border-plex-border rounded-xl"
                >
                  <h3 className="text-xs font-semibold text-plex-accent uppercase tracking-wider mb-3">
                    Research Answer
                  </h3>
                  <p className="text-sm text-plex-text whitespace-pre-wrap leading-relaxed">{finalAnswer}</p>
                </motion.div>
              )}
            </div>

            <div>
              <CapabilityDashboard />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
EOF
```

---

## STEP 10 — FINAL VERIFICATION & LAUNCH

### Full System Test

```bash
cat > scripts/test_agentic_system.sh << 'EOF'
#!/bin/bash
set -e
BASE="http://localhost:8000"
echo "=== AGENTIC SYSTEM TEST SUITE ==="

echo ""
echo "1. Health check..."
curl -sf $BASE/health | python3 -c "
import sys, json
d = json.load(sys.stdin)
assert d['status'] == 'ok', f'Health failed: {d}'
print(f'   ✓ DB: {d[\"db\"]}, Redis: {d[\"redis\"]}, Ollama: {d[\"ollama\"]}')
"

echo ""
echo "2. Capability map..."
curl -sf $BASE/agent/capability-map | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'   ✓ {len(d[\"capability_map\"])} categories tracked')
"

echo ""
echo "3. Agent run test (simple task, 30s timeout)..."
TASK='What is retrieval-augmented generation and what are its main components?'
python3 << 'PYEOF'
import asyncio, json, httpx

async def test_agent():
    events = {'sources': 0, 'thinking': 0, 'steps': 0, 'done': False}
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", "http://localhost:8000/agent/run",
            json={"task": "What is RAG?", "session_id": "test-123", "max_steps": 5}
        ) as resp:
            event_type = ""
            async for line in resp.aiter_lines():
                if line.startswith("event: "):
                    event_type = line[7:].strip()
                elif line.startswith("data: "):
                    if event_type == "agent_step": events['steps'] += 1
                    if event_type == "final_answer": events['done'] = True; break

    print(f"   ✓ Steps: {events['steps']}, Done: {events['done']}")
    assert events['steps'] > 0, "No steps executed"
    assert events['done'], "No final answer"

asyncio.run(test_agent())
PYEOF

echo ""
echo "4. Pending strategy approvals..."
curl -sf $BASE/agent/strategies/pending | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'   ✓ {d[\"count\"]} strategies pending approval')
"

echo ""
echo "=== ALL TESTS PASSED ==="
echo ""
echo "System URLs:"
echo "  API:         http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  Frontend:    http://localhost:3000"
echo "  Agent Page:  http://localhost:3000/agent"
EOF
chmod +x scripts/test_agentic_system.sh
```

### Start Everything

```bash
# Pull planning model if not done
ollama pull phi3:mini

# Build and start
docker compose up --build -d

# Watch logs
docker compose logs -f api

# Run tests after 15s startup time
sleep 15
./scripts/test_agentic_system.sh
```

---

## COMPLETION CHECKLIST — Opus Agent

```
PHASE 2 — AGENT LOOP
[ ] backend/app/agent_models.py — 6 new tables (traces, outcomes, lessons, capability, strategy, corrections)
[ ] database migration ran: init_db() creates all tables
[ ] backend/agent/tools/ — 7 tools (RAG, DuckDuckGo, ArXiv, Wikipedia, Semantic Scholar, Notepad, Finish)
[ ] backend/agent/tool_registry.py — registry validates + truncates outputs
[ ] backend/agent/context.py — AgentContext, AgentThought, StepRecord, AgentResult
[ ] backend/agent/planner.py — SINGLE action per LLM call pattern
[ ] backend/agent/goal_anchor.py — drift detection every 3 steps
[ ] backend/agent/agent_loop.py — full Think→Act→Observe loop with 5-layer intelligence

LAYER 1 — TRACE COLLECTION
[ ] backend/agent/observability/trace_collector.py — stores traces with pgvector embeddings
[ ] /agent/traces/{session_id} — returns step-by-step trace

LAYER 2 — SELF-EVALUATION
[ ] planner.cross_evaluate_step() — different model evaluates each step
[ ] agent_loop._estimate_quality() — heuristic task quality
[ ] agent_loop._detect_failure_pattern() — classifies failure type

LAYER 3 — FAILURE MEMORY
[ ] backend/agent/observability/failure_memory.py — extract lessons + inject before tasks
[ ] failure_lessons table populated after low-quality runs
[ ] /agent/daily-report — daily evolution report

LAYER 4 — GOAL DRIFT
[ ] GoalAnchor checks every 3 steps using cosine distance
[ ] Hard reset after 2 consecutive drifts

LAYER 5 — CAPABILITY + STRATEGY
[ ] backend/agent/observability/capability_map.py — success rate by task category
[ ] backend/agent/observability/strategy_library.py — learned playbooks
[ ] /agent/strategies/pending — human approval queue
[ ] /agent/strategies/{id}/approve — one-click approval

PHASE 4 — DIGITAL TWIN
[ ] backend/agent/digital_twin/evolution_protocol.py — daily review + proposals
[ ] /agent/corrections — log human overrides
[ ] user_corrections table stores training signal

FRONTEND
[ ] frontend/src/components/AgentTracePanel.tsx — step-by-step reasoning display
[ ] frontend/src/components/CapabilityDashboard.tsx — agent self-knowledge viz
[ ] frontend/src/components/StrategyApprovalPanel.tsx — strategy approval UI
[ ] frontend/src/app/agent/page.tsx — full agent page

FINAL CHECKS
[ ] ./scripts/test_agentic_system.sh passes all 4 tests
[ ] http://localhost:3000/agent renders agent page
[ ] First task creates traces in DB: SELECT COUNT(*) FROM agent_traces;
[ ] After 3 failed tasks: SELECT * FROM failure_lessons; shows lessons
[ ] /agent/capability-map returns populated records after 5+ runs
```

---

## 60-DAY BUILD TIMELINE

| Days | Milestone | Success Metric |
|------|-----------|---------------|
| 1–7 | Steps 0–2: Schema + All 7 tools | `uv run python` imports all tools |
| 8–14 | Steps 3–4: Agent loop + planner | First agent run completes in <60s |
| 15–21 | Steps 4–5: Trace collector + failure memory | Traces appear in DB |
| 22–28 | Steps 5–6: Capability map + strategy library | Approval queue works |
| 29–35 | Step 6: Agent API routes + SSE | Stream flows to frontend |
| 36–42 | Step 7: Daily evolution protocol | Daily report generates proposals |
| 43–52 | Steps 8–9: Frontend trace panel + agent page | Traces visible in browser |
| 53–60 | Collect 50+ runs, measure failure rate reduction | Compare week 1 vs week 8 |

---

## THE PAPER THIS SYSTEM PRODUCES

**Title:** *"Behavioral RSI in Agentic Systems: Observability, Process Evaluation, and Failure-Indexed Meta-Learning"*

**Your empirical claims (testable by week 8):**
1. Agents with failure memory repeat failure patterns at lower rate than agents without (measure: same failure pattern appearing in week 8 vs week 1)
2. Process-level evaluation (step scores) predicts final answer quality better than binary success/fail
3. Goal drift detection reduces task divergence in long runs (measure: cosine similarity of final answer to original task)
4. Cross-model evaluation is less circular than self-evaluation (measure: correlation with human scores)

**No other tier-3 student is running this experiment on real infrastructure. This is your edge.**

---

*Single source of truth for the Agentic Research System → Digital Twin OS build.*
*Repository: github.com/aman-bhaskar-codes/rag-research-assistant*
*Every file path is exact. Every code block is complete. Execute in order.*

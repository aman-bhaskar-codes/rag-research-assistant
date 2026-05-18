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

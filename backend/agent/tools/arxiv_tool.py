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

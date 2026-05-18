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

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

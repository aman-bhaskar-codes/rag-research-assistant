"""Routes queries to Brave, Tavily, or RAG based on focus mode."""
import asyncio
from loguru import logger
from backend.search.brave import brave_search
from backend.search.tavily import tavily_search
from backend.search.fetcher import fetch_sources_parallel
from backend.app.config import get_settings

settings = get_settings()

FOCUS_TO_SEARCH_STRATEGY = {
    "general":      "web",
    "academic":     "web",
    "code":         "web",
    "writing":      "rag",   # Only local docs
    "research":     "both",  # Web + RAG
    "documents":    "rag",
}


async def run_web_search(query: str, count: int = 8) -> list[dict]:
    """Try Brave first, fall back to Tavily."""
    sources = []

    try:
        sources = await brave_search(query, count)
        logger.debug(f"Brave returned {len(sources)} results")
    except Exception as e:
        logger.warning(f"Brave failed: {e}")

    if not sources:
        try:
            sources = await tavily_search(query, count)
            logger.debug(f"Tavily returned {len(sources)} results")
        except Exception as e:
            logger.warning(f"Tavily failed: {e}")

    return sources[:count]


async def enrich_sources(sources: list[dict]) -> list[dict]:
    """Fetch full content from each source URL in parallel."""
    if not sources:
        return sources

    urls = [s["url"] for s in sources if s.get("url")]
    contents = await fetch_sources_parallel(urls, max_concurrent=4)

    for source in sources:
        url = source.get("url", "")
        source["content"] = contents.get(url, source.get("description", ""))
        source["content_length"] = len(source["content"])

    return sources

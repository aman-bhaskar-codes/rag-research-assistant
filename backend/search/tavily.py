"""Tavily Search API — free tier: 1000 queries/month. Fallback when Brave fails."""
import httpx
from loguru import logger
from backend.app.config import get_settings

settings = get_settings()

TAVILY_URL = "https://api.tavily.com/search"


async def tavily_search(query: str, count: int = 8) -> list[dict]:
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not set, skipping Tavily search")
        return []

    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
        "max_results": min(count, 10),
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(TAVILY_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("content", "")[:300],
            "source": "tavily",
        })
    return results

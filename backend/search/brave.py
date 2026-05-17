"""Brave Search API — free tier: 2000 queries/month."""
import httpx
from loguru import logger
from backend.app.config import get_settings

settings = get_settings()

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


async def brave_search(query: str, count: int = 8) -> list[dict]:
    if not settings.brave_api_key:
        logger.warning("BRAVE_API_KEY not set, skipping Brave search")
        return []

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": settings.brave_api_key,
    }
    params = {
        "q": query,
        "count": min(count, 20),
        "search_lang": "en",
        "safesearch": "moderate",
        "freshness": "pw",  # past week
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(BRAVE_SEARCH_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("web", {}).get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "description": item.get("description", ""),
            "source": "brave",
        })
    return results

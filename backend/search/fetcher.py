"""Fetch and extract clean text content from web URLs."""
import asyncio
import httpx
import trafilatura
from loguru import logger


async def fetch_and_extract(url: str, timeout: int = 8) -> str | None:
    """Download a URL and extract its main text content."""
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Research Bot)"},
        ) as client:
            resp = await client.get(url, timeout=timeout)
            if resp.status_code != 200:
                return None
            html = resp.text

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )
        return text[:3000] if text else None  # Cap at 3000 chars per source

    except Exception as e:
        logger.debug(f"Failed to fetch {url}: {e}")
        return None


async def fetch_sources_parallel(urls: list[str], max_concurrent: int = 4) -> dict[str, str]:
    """Fetch multiple URLs concurrently. Returns {url: content} dict."""
    sem = asyncio.Semaphore(max_concurrent)

    async def fetch_one(url: str) -> tuple[str, str | None]:
        async with sem:
            content = await fetch_and_extract(url)
            return url, content

    tasks = [fetch_one(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        url: content
        for url, content in results
        if isinstance(content, str) and content
    }

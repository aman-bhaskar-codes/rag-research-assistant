from fastapi import APIRouter
import httpx
from backend.app.config import get_settings

router = APIRouter()
settings = get_settings()

AVAILABLE_MODELS = [
    {
        "id": "llama3.2:3b",
        "name": "Llama 3.2 (3B)",
        "description": "Fast, general-purpose. Best for most queries.",
        "size": "2.0 GB",
        "strengths": ["general", "fast", "reasoning"],
        "is_default": True,
    },
    {
        "id": "phi4-mini:latest",
        "name": "Phi-4 Mini",
        "description": "Microsoft. Excellent at code and math.",
        "size": "2.5 GB",
        "strengths": ["code", "math", "structured"],
        "is_default": False,
    },
    {
        "id": "qwen2.5:3b",
        "name": "Qwen 2.5 (3B)",
        "description": "Alibaba. Multilingual, strong structured output.",
        "size": "1.9 GB",
        "strengths": ["multilingual", "data", "structured"],
        "is_default": False,
    },
]


@router.get("")
async def list_models():
    """List available Ollama models with their status."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
            pulled = {m["name"] for m in resp.json().get("models", [])}
    except Exception:
        pulled = set()

    for m in AVAILABLE_MODELS:
        m["available"] = m["id"] in pulled or any(
            m["id"].split(":")[0] in p for p in pulled
        )

    return {"models": AVAILABLE_MODELS}


@router.get("/recommend")
async def recommend_model(focus: str = "general", query: str = ""):
    """Recommend the best model for a given focus mode."""
    mapping = {
        "code": "phi4-mini:latest",
        "math": "phi4-mini:latest",
        "academic": "phi4-mini:latest",
        "multilingual": "qwen2.5:3b",
        "research": "llama3.2:3b",
        "general": "llama3.2:3b",
        "writing": "llama3.2:3b",
    }
    return {"recommended": mapping.get(focus, settings.default_model)}

"""Routes queries to the right Ollama model based on focus mode and content."""
from backend.app.config import get_settings

settings = get_settings()


def select_model(focus_mode: str, requested_model: str | None = None) -> str:
    """Choose the best model for this focus mode.
    User-requested model always wins if specified.
    """
    if requested_model:
        return requested_model

    routing = {
        "code":          settings.smart_model,    # phi4-mini
        "math":          settings.smart_model,    # phi4-mini
        "academic":      settings.smart_model,    # phi4-mini
        "multilingual":  settings.multilingual_model,  # qwen2.5
        "general":       settings.fast_model,     # llama3.2
        "writing":       settings.fast_model,     # llama3.2
        "research":      settings.fast_model,     # llama3.2
        "documents":     settings.fast_model,     # llama3.2
    }
    return routing.get(focus_mode, settings.default_model)

"""
Classifies incoming tasks into categories for the capability map.
Uses fast keyword matching first, LLM fallback for ambiguous cases.
"""
import re
import ollama
from backend.app.config import get_settings

settings = get_settings()

TASK_CATEGORIES = [
    "single_fact_lookup",
    "multi_hop_research",
    "comparative_analysis",
    "paper_summarization",
    "hypothesis_generation",
    "code_explanation",
    "long_context_synthesis",
    "ambiguous_query",
]

# Fast keyword rules — avoids LLM call for obvious cases
KEYWORD_RULES = {
    "single_fact_lookup":    [r"\bwhat is\b", r"\bwho is\b", r"\bwhen did\b", r"\bdefine\b"],
    "comparative_analysis":  [r"\bcompare\b", r"\bvs\b", r"\bdifference between\b", r"\bwhich is better\b"],
    "paper_summarization":   [r"\bsummariz\b", r"\bexplain.*paper\b", r"\bwhat does.*paper\b"],
    "code_explanation":      [r"\bcode\b", r"\bfunction\b", r"\bimpleme\b", r"\bpython\b", r"\bjavascript\b"],
    "hypothesis_generation": [r"\bhypothe\b", r"\bwhat if\b", r"\bcould\b.*\bhappen\b"],
}

CLASSIFY_PROMPT = """Classify this research task into ONE category:
- single_fact_lookup: looking up a single fact
- multi_hop_research: needs multiple searches to answer
- comparative_analysis: comparing multiple things
- paper_summarization: summarizing a paper
- hypothesis_generation: generating new ideas or hypotheses
- code_explanation: explaining or debugging code
- long_context_synthesis: synthesizing many sources
- ambiguous_query: unclear or broad

Task: {task}

Output ONLY the category name, nothing else."""


async def classify_task(task: str) -> str:
    task_lower = task.lower()

    # Fast path: keyword matching
    for category, patterns in KEYWORD_RULES.items():
        for pattern in patterns:
            if re.search(pattern, task_lower):
                return category

    # Slow path: LLM classification
    try:
        client = ollama.AsyncClient(host=settings.ollama_base_url)
        resp = await client.generate(
            model=settings.fast_model,  # llama3.2 — fast, just classification
            prompt=CLASSIFY_PROMPT.format(task=task),
            options={"temperature": 0.0, "num_predict": 20},
        )
        category = resp["response"].strip().lower().replace(" ", "_")
        if category in TASK_CATEGORIES:
            return category
    except Exception:
        pass

    return "ambiguous_query"

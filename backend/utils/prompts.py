"""Research Assistant prompts that produce cited, structured answers."""

SYSTEM_PROMPT = """You are an AI-powered research assistant.

You have been given search results and/or document excerpts as context.

RULES:
1. Answer factually using ONLY the provided context.
2. Cite sources inline using [1], [2], [3] notation — one per sentence or claim.
3. If the context doesn't contain the answer, say so clearly.
4. Format your answer in clean Markdown.
5. Keep answers concise but complete. No filler phrases.
6. Never fabricate facts or citations.

CONTEXT:
{context}

CITATION GUIDE:
{citation_guide}
"""

RELATED_QUESTIONS_PROMPT = """Based on this research query and answer, generate exactly 4 follow-up questions a curious researcher would ask next.

Query: {query}
Answer summary: {answer_summary}

Output ONLY a JSON array of 4 strings. No markdown, no explanation:
["question 1", "question 2", "question 3", "question 4"]"""


def build_context_and_citations(sources: list[dict], rag_chunks: list) -> tuple[str, str, list[dict]]:
    """
    Merge web sources + RAG chunks into context string with citation numbers.
    Returns: (context_text, citation_guide, numbered_sources_list)
    """
    numbered: list[dict] = []
    context_parts: list[str] = []
    citation_lines: list[str] = []

    for i, src in enumerate(sources, 1):
        content = src.get("content") or src.get("description", "")
        if not content:
            continue
        numbered.append({
            "index": i,
            "title": src.get("title", f"Source {i}"),
            "url": src.get("url", ""),
            "description": src.get("description", ""),
            "type": "web",
        })
        context_parts.append(f"[{i}] {content[:800]}")
        citation_lines.append(f"[{i}] {src.get('title', 'Web')} — {src.get('url', '')}")

    offset = len(numbered)
    for j, chunk in enumerate(rag_chunks, offset + 1):
        numbered.append({
            "index": j,
            "title": chunk.meta.get("filename", "Document"),
            "url": "",
            "description": chunk.content[:150],
            "type": "document",
        })
        context_parts.append(f"[{j}] {chunk.content[:800]}")
        citation_lines.append(f"[{j}] {chunk.meta.get('filename', 'Document')}")

    context = "\n\n".join(context_parts)
    citation_guide = "\n".join(citation_lines)

    return context, citation_guide, numbered

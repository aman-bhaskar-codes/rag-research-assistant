from typing import List, Dict


def recall_at_k(chunks: List[Dict], expected_keywords: List[str]) -> float:
    """
    Checks how many expected keywords appear in retrieved chunks.
    This metric ensures the retrieval system is capturing core conceptual knowledge.
    """

    hits = 0

    for keyword in expected_keywords:
        keyword = keyword.lower()

        # Check if the keyword exists in ANY of the retrieved chunks
        found = any(keyword in chunk["content"].lower() for chunk in chunks)

        if found:
            hits += 1

    # avoid division by zero
    if len(expected_keywords) == 0:
        return 0.0

    return hits / len(expected_keywords)

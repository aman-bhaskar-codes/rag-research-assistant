import typing
from typing import List, Dict, Any


def reciprocal_rank_fusion(results_list: List[List[Dict[str, Any]]], k: int = 60) -> List[str]:
    """
    Combines sorted results from multiple retrievers using Reciprocal Rank Fusion (RRF).
    
    Args:
        results_list: A list where each element is a list of results (chunks) from a retriever.
        k: The constant used in the RRF formula to prevent dominating scores.
        
    Returns:
        List of doc_ids sorted by their fused scores.
    """
    scores = {}

    for results in results_list:
        for rank, item in enumerate(results):
            # Production Standard: Always use the standardized chunk_id
            doc_id = item.get("metadata", {}).get("chunk_id", item["content"])

            if doc_id not in scores:
                scores[doc_id] = 0.0

            scores[doc_id] += 1.0 / (k + rank)

    # Sort by fused score descending
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [item[0] for item in sorted_items]

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
            # Fallback to pure content if a unique chunk_id is unavailable.
            # Using source_file + chunk_index combines to a perfect ID if ingested through our engine.
            meta = item.get("metadata", {})
            source_file = meta.get("source_file", "unknown")
            chunk_index = meta.get("chunk_index", "unknown")
            
            if source_file != "unknown" and chunk_index != "unknown":
                doc_id = f"{source_file}::{chunk_index}"
            else:
                doc_id = item["content"]

            if doc_id not in scores:
                scores[doc_id] = 0

            scores[doc_id] += 1 / (k + rank)

    # Sort by fused score descending
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [item[0] for item in sorted_items]

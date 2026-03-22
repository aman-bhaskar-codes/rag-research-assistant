from typing import List, Dict


def normalize_scores(chunks: List[Dict]) -> List[Dict]:
    """
    Performs Min-Max normalization on chunk scores.
    Ensures different retrieval strategies (Vector vs Keyword) are 
    comparable before fusion or reranking.
    """
    if not chunks:
        return []
        
    scores = [c["score"] for c in chunks]
    min_s = min(scores)
    max_s = max(scores)
    
    # Avoid division by zero
    if max_s == min_s:
        for c in chunks:
            c["score"] = 1.0
        return chunks
        
    for c in chunks:
        c["score"] = (c["score"] - min_s) / (max_s - min_s)
        
    return chunks

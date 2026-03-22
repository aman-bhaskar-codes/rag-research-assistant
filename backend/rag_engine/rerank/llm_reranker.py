import logging
import re
from typing import List, Dict, Any
from .base import BaseReranker

logger = logging.getLogger(__name__)


class LLMReranker(BaseReranker):
    """
    Production-grade LLM Reranker.
    Replaces rudimentary single-chunk scoring with an ultra-efficient
    concatenated batch-prompt mechanism. Translates fuzzy Vector/Keyword
    recall into absolute intent-alignment precision.
    """
    
    def __init__(self, llm):
        self.llm = llm

    async def rerank(self, query: str, chunks: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        # Guard against empty retrievals
        if not chunks:
            return []
            
        # Top-K constraint logic in case the input chunks are too few to rerank
        if len(chunks) <= top_n:
            return chunks

        prompt = f"""
You are an advanced relevance ranking system.

Rank the following numbered text chunks based on their direct relevance in answering the user's query.

Query: "{query}"

Chunks:
"""
        # Batch concatenation strategy to minimize LLM overhead/cost.
        # Limit the snippet size to avoid context window explosion on K=20 chunks.
        for i, chunk in enumerate(chunks):
            snippet = str(chunk.get("content", ""))[:300].replace('\n', ' ')
            prompt += f"\n[{i}] {snippet}"

        prompt += "\n\nAnalyze the chunks and return ONLY their integer indices sorted by highest relevance to lowest relevance. Do not output any other text or reasoning. Example format: 2 0 4 1 3"

        response = await self.llm.generate(prompt)

        # Robust defensive parsing.
        # LLMs frequently hallucinate surrounding text despite strict instructions.
        try:
            # Extract only numeric tokens from the response
            raw_tokens = re.findall(r'\d+', response)
            
            # Convert to integers, preserving the sorted order from the LLM. 
            # We use a set observation to deduplicate if the LLM hallucinated duplicate IDs.
            seen = set()
            indices = []
            for token in raw_tokens:
                idx = int(token)
                if idx not in seen and idx < len(chunks):
                    seen.add(idx)
                    indices.append(idx)
                    
            # If the LLM completely failed to return valid numbers, fallback 
            if not indices:
                indices = list(range(len(chunks)))
                
        except Exception as e:
            logger.error(f"Failed to parse LLM rerank output: {response}. Error: {e}")
            # Fallback to the original hybrid retriever ranking (which is still decent)
            indices = list(range(len(chunks)))

        # Append any chunks the LLM missed to the end of the ranking list
        # ensuring we still have enough chunks to return `top_n`
        for i in range(len(chunks)):
            if i not in seen:
                indices.append(i)

        # Assemble finalized precision output
        ranked = [chunks[i] for i in indices]
        return ranked[:top_n]

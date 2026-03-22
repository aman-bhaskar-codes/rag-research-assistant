import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any

from rag_engine.embeddings.base import BaseEmbedder
from rag_engine.embeddings.ollama_embedder import OllamaEmbedder


class FaissRetriever:
    """
    Handles similarity search against a FAISS vector index.
    """
    def __init__(self, index_path: str, chunks_path: str, embedder: BaseEmbedder = None):
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.embedder = embedder or OllamaEmbedder(model_name="nomic-embed-text")
        
        self.index = None
        self.chunks = []
        self._load_store()

    def _load_store(self):
        """Load the FAISS index and chunk metadata from disk."""
        if not os.path.exists(self.index_path) or not os.path.exists(self.chunks_path):
            raise FileNotFoundError(
                f"Vector store not found. Ensure {self.index_path} and {self.chunks_path} exist. "
                "Have you run the ingestion pipeline?"
            )
            
        print(f"Loading FAISS index from {self.index_path}...")
        self.index = faiss.read_index(self.index_path)
        
        print(f"Loading chunk metadata from {self.chunks_path}...")
        with open(self.chunks_path, "r") as f:
            self.chunks = json.load(f)
            
        if self.index.ntotal != len(self.chunks):
            print(f"⚠️ Warning: Index size ({self.index.ntotal}) does not match chunk count ({len(self.chunks)}).")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Embed the query and perform a similarity search.
        
        Args:
            query: The search text
            top_k: Number of results to return
            
        Returns:
            List of dictionaries containing the chunk text, source metadata, and similarity score.
        """
        if not self.index:
            raise RuntimeError("FAISS index not loaded.")
            
        # 1. Embed the query
        print(f"Embedding query: '{query}'...")
        query_vector = self.embedder.embed_text(query)
        
        # FAISS expects a 2D float32 array: shape (1, dimension)
        xq = np.array([query_vector]).astype('float32')
        
        # 2. Search the index (L2 distance)
        # distances: shape (1, top_k), indices: shape (1, top_k)
        distances, indices = self.index.search(xq, top_k)
        
        # 3. Format results
        results = []
        for i, idx in enumerate(indices[0]):
            # FAISS returns -1 if there are fewer vectors than top_k
            if idx == -1:
                continue
                
            chunk_data = self.chunks[idx].copy()
            
            # Since FAISS IndexFlatL2 uses Euclidean distance, lower is better.
            # We convert distance to a loose "similarity" score for display purposes.
            # (In Euclidean space, 0 is perfect match).
            chunk_data["l2_distance"] = float(distances[0][i])
            results.append(chunk_data)
            
        return results

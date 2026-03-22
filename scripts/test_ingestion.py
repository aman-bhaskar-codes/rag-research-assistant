import sys
import os
import numpy as np
import faiss
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

# Add backend directory to module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.loaders.text_loader import TextLoader
from rag_engine.processing.cleaner import TextCleaner
from rag_engine.chunking.recursive_chunker import RecursiveCharacterChunker
from rag_engine.embeddings.gemini_embedder import GeminiEmbedder

def main():
    print("🚀 Starting Ingestion Pipeline Test...")

    # 1. Load Data
    loader = TextLoader()
    text_path = "data/ai_ml/articles/sample.txt"
    print(f"📄 Loading text from {text_path}...")
    text = loader.load(text_path)

    # 2. Clean Data
    print("🧹 Cleaning text...")
    cleaner = TextCleaner()
    cleaned_text = cleaner.clean(text)

    # 3. Chunk Data
    print("✂️ Chunking text into overlapping windows...")
    chunker = RecursiveCharacterChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk(cleaned_text)
    print(f"✅ Created {len(chunks)} chunks.")
    for i, chunk in enumerate(chunks[:2]):
         print(f"   🔹 Chunk {i+1} ({len(chunk)} chars): {chunk[:80]}...")

    # 4. Embed Data
    print("🧠 Generating embeddings with Gemini...")
    try:
        embedder = GeminiEmbedder()
        embeddings = embedder.embed_documents(chunks)
        print(f"✅ Generated {len(embeddings)} embeddings vectors.")
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return

    # 5. Indexing (FAISS)
    print("📂 Creating FAISS Vector Index...")
    dimension = len(embeddings[0])
    # Convert list to numpy float32 matrix
    xb = np.array(embeddings).astype('float32')

    # IndexFlatL2 measures L2 distance
    index = faiss.IndexFlatL2(dimension)
    index.add(xb)
    
    print(f"✅ Index built with {index.ntotal} vectors.")

    # Save mapping of vector index to chunk text for retrieval lookups
    os.makedirs("data/vector_store", exist_ok=True)
    index_path = "data/vector_store/index.faiss"
    faiss.write_index(index, index_path)
    print(f"💾 Vector Index saved to {index_path}")

    # Save chunk texts for retrieval stage
    import json
    with open("data/vector_store/chunks.json", "w") as f:
        json.dump(chunks, f)

    print("\n🎉 INGESTION SUCCESSFUL!")

if __name__ == "__main__":
    main()

import sys
import os

# Add backend directory to module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.loaders.text_loader import TextLoader
from rag_engine.processing.cleaner import TextCleaner
from rag_engine.chunking.recursive_chunker import RecursiveCharacterChunker

def main():
    print("📊 Chunking Statistics Diagnostics...")

    # Load file
    loader = TextLoader()
    text_path = "data/ai_ml/articles/sample_large.txt"
    
    # Create a large sample text file (~5000 chars) for rich testing
    large_text = """
The Transformer architecture, introduced by Vaswani et al. in 2017, completely revolutionized the field of Natural Language Processing (NLP). Before Transformers, recurrent neural networks (RNNs) and Long Short-Term Memory (LSTM) networks were the state-of-the-art for sequence modeling tasks like translation and text generation. However, RNNs suffered from fundamental bottlenecks: they processed tokens sequentially, making parallelization during training impossible, and had difficulty maintaining long-range dependencies because of gradient vanishing problems.

Transformers solved this using the Self-Attention Mechanism. Instead of viewing tokens sequentially, the model looks at all tokens simultaneously and calculates weights defining the relationship between each word. This allows "parallel" training on massive GPU clusters and enables capturing dense contextual relationships (e.g., matching a pronoun on page 10 to a noun on page 1). 

Following Transformers, Large Language Models (LLMs) scaling laws took over. Enterprises built BERT (Encoder-only) for classification and GPT (Decoder-only) for text generation. These models contain billions of parameters trained on trillions of words from the internet, books, and articles. They understand syntax, structure, and can generate highly cohesive essays or modular software code scripts.

But dense scaling hit memory boundaries. As prompt limits expanded to 100K+ tokens, token lookup speeds dropped. This created the need for Retrieval-Augmented Generation (RAG). RAG bridges the gap between static model weights and dynamic, real-time proprietary data. Instead of feeding a 100-page document into the context window, RAG chops the document into chunks, embeds them into numbers, and searches for the top matching sections inside a Vector Index.

Chunking is the single most critical component of RAG. Highly fragmented chunks (like 140 characters) lose sentence structure and break reference indexes. Excessively large chunks (like 3000 chars) overwhelm the LLM with unnecessary noise and increase inference latency. Modern RAGs utilize Recursive Character Chunking to split on semantic boundary marks like double-newlines, retaining cohesive logical paragraphs without exceeding static window sizes.
""" * 5 # Replicating 5 times to create a heavy corpus

    os.makedirs("data/ai_ml/articles", exist_ok=True)
    with open(text_path, "w") as f:
        f.write(large_text)

    text = loader.load(text_path)

    # Clean
    cleaner = TextCleaner()
    cleaned_text = cleaner.clean(text)

    # Chunk 
    print("🔄 Splitting text using RecursiveCharacterChunker (Size: 1000, Overlap: 200)...")
    chunker = RecursiveCharacterChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.chunk(cleaned_text)

    lengths = [len(c) for c in chunks]

    print("\n✅ Statistics:")
    print("=" * 30)
    print(f"Total Chunks: {len(chunks)}")
    print(f"Min Size:     {min(lengths)}")
    print(f"Max Size:     {max(lengths)}")
    print(f"Avg Size:     {sum(lengths)//len(lengths)}")
    print("=" * 30)

    print("\n🔹 Sample Chunks lengths:")
    for i, c in enumerate(chunks):
         print(f"   Chunk {i+1}: {len(c)} chars")

if __name__ == "__main__":
    main()

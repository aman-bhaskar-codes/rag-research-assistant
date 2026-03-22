import sys
import os

# Add backend directory to module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.loaders.text_loader import TextLoader
from rag_engine.processing.cleaner import TextCleaner
from rag_engine.chunking.recursive_chunker import RecursiveCharacterChunker

def main():
    print("✂️ Starting Isolated Chunking Test...")

    # Load file
    loader = TextLoader()
    text_path = "data/ai_ml/articles/sample.txt"
    if not os.path.exists(text_path):
         print(f"❌ Document {text_path} not found. Running with mock text...")
         text = "Large language models (LLMs) are artificial intelligence systems trained on vast amounts of text data to generate human-like text outputs. " * 30
    else:
         text = loader.load(text_path)

    # Clean
    cleaner = TextCleaner()
    cleaned_text = cleaner.clean(text)

    # Chunk 
    print("🔄 Splitting text using RecursiveCharacterChunker...")
    # Using small size to force multiple splits for descriptive printing
    chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk(cleaned_text)

    print(f"\n✅ Created {len(chunks)} chunks total.")
    print("="*40)
    
    for i, chunk in enumerate(chunks):
         print(f"\n🔹 [CHUNK {i+1}] ({len(chunk)} characters):")
         print(f"   {chunk}")
         print("-" * 20)

if __name__ == "__main__":
    main()

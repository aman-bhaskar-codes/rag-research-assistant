import os
import sys

# ✅ Add project root to path (clean fix)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from rag_engine.loaders.pdf_loader import PDFLoader
from rag_engine.loaders.text_loader import TextLoader
from rag_engine.processing.cleaner import TextCleaner
from rag_engine.chunking.factory import get_chunker


def test_pipeline():
    # -------- INIT --------
    pdf_loader = PDFLoader()
    text_loader = TextLoader()
    cleaner = TextCleaner()

    chunker = get_chunker("research")

    # -------- FILE PATH --------
    pdf_path = "data/ai_ml/pdfs/sample.pdf"
    txt_path = "data/ai_ml/articles/sample.txt"

    # -------- LOAD --------
    print("\n📥 Loading PDF...")
    pdf_text = pdf_loader.load(pdf_path)
    print(f"PDF length: {len(pdf_text)}")

    print("\n📥 Loading TXT...")
    txt_text = text_loader.load(txt_path)
    print(f"TXT length: {len(txt_text)}")

    # -------- CLEAN --------
    print("\n🧹 Cleaning PDF...")
    clean_pdf = cleaner.clean(pdf_text)

    # -------- CHUNK --------
    print("\n✂️ Chunking...")
    chunks = chunker.split(clean_pdf)

    print(f"\n✅ Total chunks: {len(chunks)}")

    # -------- PREVIEW --------
    print("\n🔍 Sample Chunk:\n")
    print(chunks[0][:500])


if __name__ == "__main__":
    test_pipeline()
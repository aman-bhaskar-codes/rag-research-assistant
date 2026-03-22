import sys
import os
import json
import time
import numpy as np
import faiss
from dotenv import load_dotenv

load_dotenv()

# Add backend directory to module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from rag_engine.loaders.pdf_loader import PDFLoader
from rag_engine.loaders.text_loader import TextLoader
from rag_engine.processing.cleaner import TextCleaner
from rag_engine.chunking.recursive_chunker import RecursiveCharacterChunker
from rag_engine.embeddings.ollama_embedder import OllamaEmbedder


# ═══════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════
DATA_DIR = "backend/rag_engine/data/ai_ml"
PDF_DIR = os.path.join(DATA_DIR, "ai_ml_pdfs")
TXT_DIR = os.path.join(DATA_DIR, "ai_ml_articles_txt")
VECTOR_STORE_DIR = "data/vector_store"
CHECKPOINT_FILE = os.path.join(VECTOR_STORE_DIR, "checkpoint.json")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 5       # Process 5 files at a time
MAX_RETRIES = 3      # Max retries per embedding call
BASE_WAIT = 10       # Base wait seconds for retry backoff


def discover_files():
    """Discover all PDF and TXT files."""
    pdfs = []
    txts = []
    
    if os.path.exists(PDF_DIR):
        for f in sorted(os.listdir(PDF_DIR)):
            if f.lower().endswith(".pdf"):
                pdfs.append(os.path.join(PDF_DIR, f))
    
    if os.path.exists(TXT_DIR):
        for f in sorted(os.listdir(TXT_DIR)):
            if f.lower().endswith(".txt"):
                txts.append(os.path.join(TXT_DIR, f))
    
    return pdfs, txts


def load_file(filepath: str) -> str:
    if filepath.lower().endswith(".pdf"):
        loader = PDFLoader()
    else:
        loader = TextLoader()
    return loader.load(filepath)


def load_checkpoint():
    """Load checkpoint to resume from where we left off."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return None


def save_checkpoint(chunks, embeddings, files_done):
    """Save checkpoint for resume capability."""
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    checkpoint = {
        "chunks": chunks,
        "embeddings_count": len(embeddings),
        "files_done": files_done,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f)


def embed_single_with_retry(embedder: OllamaEmbedder, text: str, chunk_idx: int, total: int):
    """Embed a single text with exponential backoff retry."""
    for attempt in range(MAX_RETRIES):
        try:
            embedding = embedder.embed_text(text)
            return embedding
        except Exception as e:
            error_str = str(e)
            wait_time = BASE_WAIT * (2 ** attempt)  # 10, 20, 40s
            print(f"      ⏳ Server error: {error_str}. "
                  f"Waiting {wait_time}s (attempt {attempt+1}/{MAX_RETRIES})...")
            time.sleep(wait_time)
    raise RuntimeError(f"Failed after {MAX_RETRIES} retries for chunk {chunk_idx}")


def process_and_chunk_file(filepath, cleaner, chunker):
    """Load, clean, and chunk a single file."""
    filename = os.path.basename(filepath)
    try:
        raw_text = load_file(filepath)
        cleaned_text = cleaner.clean(raw_text)
        chunks = chunker.chunk(cleaned_text)
        
        chunk_records = []
        for i, chunk_text in enumerate(chunks):
            chunk_records.append({
                "text": chunk_text,
                "source_file": filename,
                "source_path": filepath,
                "chunk_index": i,
                "chunk_length": len(chunk_text),
            })
        return chunk_records
    except Exception as e:
        print(f"      ❌ Error loading {filename}: {e}")
        return []


def main():
    print("=" * 60)
    print("🚀 BULK INGESTION PIPELINE (with Resume & Retry)")
    print("=" * 60)
    print(f"   Chunk Size:    {CHUNK_SIZE} chars")
    print(f"   Chunk Overlap: {CHUNK_OVERLAP} chars")
    print(f"   Batch Size:    {BATCH_SIZE} files")
    print(f"   Max Retries:   {MAX_RETRIES} per embedding")
    print()
    
    # ── Step 1: Discover Files ──
    print("📂 STEP 1: Discovering files...")
    pdfs, txts = discover_files()
    all_files = pdfs + txts
    print(f"   Found {len(pdfs)} PDFs + {len(txts)} TXTs = {len(all_files)} total files")
    
    if not all_files:
        print("❌ No files found. Exiting.")
        return
    
    # ── Check for checkpoint (resume) ──
    checkpoint = load_checkpoint()
    all_chunks = []
    all_embeddings = []
    files_already_done = set()
    
    if checkpoint:
        files_already_done = set(checkpoint.get("files_done", []))
        print(f"\n🔄 RESUMING from checkpoint!")
        print(f"   Files already done: {len(files_already_done)}")
        print(f"   Chunks saved: {len(checkpoint.get('chunks', []))}")
        
        # Reload saved chunks and re-embed them from the chunks.json if it exists
        chunks_path = os.path.join(VECTOR_STORE_DIR, "chunks_partial.json")
        embeddings_path = os.path.join(VECTOR_STORE_DIR, "embeddings_partial.npy")
        if os.path.exists(chunks_path):
            with open(chunks_path, "r") as f:
                all_chunks = json.load(f)
        if os.path.exists(embeddings_path):
            all_embeddings = np.load(embeddings_path).tolist()
        
        print(f"   Loaded {len(all_chunks)} chunks, {len(all_embeddings)} embeddings")
        
        # Filter out already processed files
        remaining_files = [f for f in all_files if os.path.basename(f) not in files_already_done]
        print(f"   Remaining files: {len(remaining_files)}")
    else:
        remaining_files = all_files
    
    if not remaining_files:
        print("\n✅ All files already processed! Building final index...")
    else:
        # ── Step 2: Initialize Components ──
        print("\n⚙️  STEP 2: Initializing components...")
        cleaner = TextCleaner()
        chunker = RecursiveCharacterChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        embedder = OllamaEmbedder(model_name="nomic-embed-text")
        print("   ✅ Cleaner, Chunker, Embedder ready")
        
        # ── Step 3: Process in Batches ──
        batches = [remaining_files[i:i+BATCH_SIZE] for i in range(0, len(remaining_files), BATCH_SIZE)]
        
        for batch_idx, batch_files in enumerate(batches):
            batch_num = batch_idx + 1
            print(f"\n{'─' * 60}")
            print(f"📦 BATCH {batch_num}/{len(batches)} ({len(batch_files)} files)")
            print(f"{'─' * 60}")
            
            # ── Chunk all files in batch ──
            print(f"\n   ✂️  Chunking batch {batch_num}...")
            batch_chunks = []
            for filepath in batch_files:
                filename = os.path.basename(filepath)
                print(f"   📄 Loading: {filename}")
                file_chunks = process_and_chunk_file(filepath, cleaner, chunker)
                if file_chunks:
                    batch_chunks.extend(file_chunks)
                    avg = sum(c["chunk_length"] for c in file_chunks) // max(len(file_chunks), 1)
                    print(f"      ✅ {len(file_chunks)} chunks (avg {avg} chars)")
            
            if not batch_chunks:
                print(f"   ⚠️  No chunks generated for batch {batch_num}")
                continue
            
            # ── Stats ──
            lengths = [c["chunk_length"] for c in batch_chunks]
            print(f"\n   📊 Batch {batch_num} Stats:")
            print(f"      Total Chunks: {len(batch_chunks)}")
            print(f"      Min Size:     {min(lengths)} chars")
            print(f"      Max Size:     {max(lengths)} chars")
            print(f"      Avg Size:     {sum(lengths)//len(lengths)} chars")
            
            # ── Embed with retry ──
            print(f"\n   🧠 Embedding batch {batch_num} ({len(batch_chunks)} chunks)...")
            batch_embeddings = []
            failed = False
            
            for i, chunk in enumerate(batch_chunks):
                try:
                    embedding = embed_single_with_retry(
                        embedder, chunk["text"], i+1, len(batch_chunks)
                    )
                    batch_embeddings.append(embedding)
                    
                    if (i + 1) % 10 == 0 or i == len(batch_chunks) - 1:
                        print(f"      ✅ Embedded {i+1}/{len(batch_chunks)}")
                    
                    # No rate limit needed for local Ollama
                    pass
                        
                except Exception as e:
                    print(f"      ❌ Fatal error at chunk {i+1}: {e}")
                    print(f"      💾 Saving partial progress...")
                    # Save what we have so far
                    all_chunks.extend(batch_chunks[:i])
                    all_embeddings.extend(batch_embeddings)
                    files_done_now = list(files_already_done) + [os.path.basename(f) for f in batch_files]
                    save_partial(all_chunks, all_embeddings, files_done_now)
                    failed = True
                    break
            
            if failed:
                print(f"\n   ⚠️  Batch {batch_num} partially saved. Re-run to resume.")
                break
            
            # Batch success — save progress
            all_chunks.extend(batch_chunks)
            all_embeddings.extend(batch_embeddings)
            for f in batch_files:
                files_already_done.add(os.path.basename(f))
            
            print(f"   ✅ Batch {batch_num} complete: {len(batch_chunks)} chunks → {len(batch_embeddings)} vectors")
            
            # Save checkpoint after each batch
            save_partial(all_chunks, all_embeddings, list(files_already_done))
            
            # Small pause between batches
            if batch_idx < len(batches) - 1:
                print("   ⏳ Next batch starting...")
                time.sleep(3)
    
    # ── Step 4: Build FAISS Index ──
    if not all_embeddings:
        print("\n❌ No embeddings generated. Exiting.")
        return
    
    print(f"\n{'=' * 60}")
    print(f"📂 STEP 4: Building FAISS Vector Index")
    print(f"{'=' * 60}")
    
    dimension = len(all_embeddings[0])
    xb = np.array(all_embeddings).astype('float32')
    
    index = faiss.IndexFlatL2(dimension)
    index.add(xb)
    
    print(f"   ✅ Index built: {index.ntotal} vectors, {dimension}-dimensional")
    
    # ── Step 5: Save Everything ──
    print(f"\n💾 STEP 5: Saving to disk...")
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    index_path = os.path.join(VECTOR_STORE_DIR, "index.faiss")
    faiss.write_index(index, index_path)
    print(f"   ✅ FAISS index → {index_path}")
    
    chunks_path = os.path.join(VECTOR_STORE_DIR, "chunks.json")
    with open(chunks_path, "w") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"   ✅ Chunk metadata → {chunks_path}")
    
    manifest = {
        "total_files": len(all_files),
        "total_chunks": len(all_chunks),
        "total_vectors": len(all_embeddings),
        "vector_dimension": dimension,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "files_processed": list(files_already_done),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    manifest_path = os.path.join(VECTOR_STORE_DIR, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"   ✅ Manifest → {manifest_path}")
    
    # Clean up checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
    for tmp in ["chunks_partial.json", "embeddings_partial.npy"]:
        p = os.path.join(VECTOR_STORE_DIR, tmp)
        if os.path.exists(p):
            os.remove(p)
    
    # ── Final Summary ──
    print(f"\n{'=' * 60}")
    print(f"🎉 INGESTION COMPLETE!")
    print(f"{'=' * 60}")
    print(f"   📄 Files Processed:  {len(files_already_done)}")
    print(f"   ✂️  Total Chunks:     {len(all_chunks)}")
    print(f"   🧠 Total Vectors:    {len(all_embeddings)}")
    print(f"   📐 Vector Dimension: {dimension}")
    print(f"   💾 Index Size:       {os.path.getsize(index_path) / 1024:.1f} KB")
    print(f"   📁 Stored in:        {VECTOR_STORE_DIR}/")
    print(f"{'=' * 60}")


def save_partial(chunks, embeddings, files_done):
    """Save partial progress for resume."""
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    with open(os.path.join(VECTOR_STORE_DIR, "chunks_partial.json"), "w") as f:
        json.dump(chunks, f)
    
    if embeddings:
        np.save(os.path.join(VECTOR_STORE_DIR, "embeddings_partial.npy"), 
                np.array(embeddings).astype('float32'))
    
    checkpoint = {
        "files_done": files_done,
        "chunks_count": len(chunks),
        "embeddings_count": len(embeddings),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"   💾 Checkpoint saved: {len(chunks)} chunks, {len(embeddings)} embeddings, {len(files_done)} files")


if __name__ == "__main__":
    main()

import os
import shutil
from pathlib import Path

def clean_project():
    print("🚀 Initiating Final GitHub Polish...")
    root = Path(__file__).parent

    # 1. Delete all __pycache__ and .DS_Store globally
    delete_count = 0
    for file_path in root.rglob("*.DS_Store"):
        os.remove(file_path)
        delete_count += 1
        
    for cache_dir in root.rglob("__pycache__"):
        shutil.rmtree(cache_dir)
        delete_count += 1
    
    print(f"✅ Wiped {delete_count} junk cache and OS files.")

    # 2. Delete redundant root rag_engine copy (if exists, since actual one is in backend/rag_engine)
    root_rag = root / "rag_engine"
    if root_rag.exists() and root_rag.is_dir():
        shutil.rmtree(root_rag)
        print("✅ Removed redundant root `rag_engine` folder (real logic lives in `backend/`).")

    # 3. Delete redundant production README
    prod_readme = root / "README_PRODUCTION.md"
    if prod_readme.exists():
        os.remove(prod_readme)
        print("✅ Removed redundant `README_PRODUCTION.md` (main README is now the master doc).")

    print("\n🎉 Project is PRISTINE. You are ready to push to GitHub!")
    print("Run =>  `git add . && git commit -m 'Initial production launch' && git push`")

if __name__ == "__main__":
    clean_project()

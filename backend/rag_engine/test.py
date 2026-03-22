from rag_engine.loaders.pdf_loader import PDFLoader
from rag_engine.loaders.text_loader import TextLoader

pdf_loader = PDFLoader()
text_loader = TextLoader()

pdf_text = pdf_loader.load("data/ai_ml/pdfs/sample.pdf")
txt_text = text_loader.load("data/ai_ml/articles/sample.txt")

print("PDF preview:\n", pdf_text[:500])
print("\n---\n")
print("TXT preview:\n", txt_text[:500])
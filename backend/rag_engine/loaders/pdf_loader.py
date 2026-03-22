import pdfplumber
from .base import BaseLoader


class PDFLoader(BaseLoader):
    def load(self, file_path: str) -> str:
        try:
            all_text = []

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()

                    if text:
                        # Clean page-level noise
                        text = text.strip()
                        all_text.append(text)

            full_text = "\n\n".join(all_text)

            # Global cleaning
            full_text = self._clean_text(full_text)

            return full_text

        except Exception as e:
            raise RuntimeError(f"Error loading PDF {file_path}: {e}")

    def _clean_text(self, text: str) -> str:
        # Remove excessive newlines
        text = text.replace("\n\n\n", "\n\n")

        # Fix broken lines (common in PDFs)
        text = text.replace("-\n", "")  # hyphenated words
        text = text.replace("\n", " ")

        # Normalize spaces
        text = " ".join(text.split())

        return text
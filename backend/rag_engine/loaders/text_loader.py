from .base import BaseLoader


class TextLoader(BaseLoader):
    def load(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Basic cleaning
            text = text.strip()

            return text

        except Exception as e:
            raise RuntimeError(f"Error loading text file {file_path}: {e}")
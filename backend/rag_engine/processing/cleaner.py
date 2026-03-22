from .rules import (
    remove_references_section,
    remove_citations,
    normalize_whitespace,
    remove_urls,
)


class TextCleaner:
    def __init__(self):
        pass

    def clean(self, text: str) -> str:
        text = remove_references_section(text)
        text = remove_citations(text)
        text = remove_urls(text)
        text = normalize_whitespace(text)

        return text
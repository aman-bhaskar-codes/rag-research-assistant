from .base import BaseChunker

class RecursiveCharacterChunker(BaseChunker):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: list[str] = None):
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        def _split_text(text: str, separators: list[str]) -> list[str]:
            if not separators:
                # If no more separators, just force split by size
                return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

            separator = separators[0]
            next_separators = separators[1:]

            if separator == "":
                # Character split fallback
                splits = list(text)
            else:
                splits = text.split(separator)

            final_chunks = []
            current_buffer = []
            current_count = 0

            for split in splits:
                # Add separator back except for empty string
                item = split + (separator if separator != "" else "")
                item_len = len(item)

                if item_len > self.chunk_size:
                    # If single item exceeds size, process left-overs with next separator
                    if current_buffer:
                        final_chunks.append("".join(current_buffer))
                        current_buffer = []
                        current_count = 0
                    final_chunks.extend(_split_text(item, next_separators))
                    continue

                if current_count + item_len > self.chunk_size:
                    if current_buffer:
                        final_chunks.append("".join(current_buffer))
                        
                        # Add overlap to new buffer if possible
                        overlap_buffer = []
                        overlap_count = 0
                        for j in reversed(current_buffer):
                            if overlap_count + len(j) <= self.chunk_overlap:
                                overlap_buffer.insert(0, j)
                                overlap_count += len(j)
                            else:
                                break
                        current_buffer = overlap_buffer
                        current_count = overlap_count

                current_buffer.append(item)
                current_count += item_len

            if current_buffer:
                chunk_str = "".join(current_buffer)
                # If the last chunk is too small, absorb it into the previous chunk 
                if final_chunks and len(chunk_str) < self.chunk_overlap:
                    final_chunks[-1] = final_chunks[-1] + chunk_str
                else:
                    final_chunks.append(chunk_str)

            return final_chunks

        return _split_text(text, self.separators)

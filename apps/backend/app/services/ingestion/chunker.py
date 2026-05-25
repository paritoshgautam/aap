from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str
    token_estimate: int


class TextChunker:
    def __init__(self, chunk_size: int, overlap: int) -> None:
        if overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[TextChunk]:
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if not normalized:
            return []

        chunks: list[TextChunk] = []
        start = 0
        index = 0
        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            if end < len(normalized):
                boundary = max(normalized.rfind("\n", start, end), normalized.rfind(". ", start, end))
                if boundary > start + int(self.chunk_size * 0.6):
                    end = boundary + 1
            chunk_text = normalized[start:end].strip()
            if chunk_text:
                chunks.append(
                    TextChunk(
                        index=index,
                        text=chunk_text,
                        token_estimate=max(1, len(chunk_text) // 4),
                    )
                )
                index += 1
            if end >= len(normalized):
                break
            start = max(0, end - self.overlap)
        return chunks

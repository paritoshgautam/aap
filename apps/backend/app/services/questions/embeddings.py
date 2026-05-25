import math

from openai import AsyncOpenAI


class EmbeddingService:
    def __init__(self, api_key: str | None, model: str = "text-embedding-3-small") -> None:
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def embed(self, text: str) -> list[float] | None:
        if self.client is None:
            return None
        response = await self.client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)

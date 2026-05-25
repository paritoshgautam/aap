import json
from pathlib import Path

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from app.core.config import Settings
from app.models.curriculum import SourceChunk, Topic
from app.models.question import QuestionType
from app.schemas.question import GeneratedQuestionItem, QuestionGenerateRequest


class GeneratedQuestionBatch(BaseModel):
    questions: list[GeneratedQuestionItem] = Field(default_factory=list)


class QuestionGenerationError(RuntimeError):
    pass


class OpenAIQuestionGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.prompt_path = Path(__file__).parents[2] / "prompts" / "question_generation.v1.json"
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def generate(
        self,
        topic: Topic,
        chunks: list[SourceChunk],
        request: QuestionGenerateRequest,
    ) -> GeneratedQuestionBatch:
        if self.client is None:
            raise QuestionGenerationError("OPENAI_API_KEY is required for question generation")

        prompt = json.loads(self.prompt_path.read_text(encoding="utf-8"))
        context = self._format_context(chunks)
        user_payload = {
            "topic": {
                "id": str(topic.id),
                "code": topic.code,
                "title": topic.title,
                "description": topic.description,
                "ib_metadata": topic.ib_metadata,
            },
            "question_type": request.question_type,
            "count": request.count,
            "difficulty_target": request.difficulty_target,
            "blooms_levels": request.blooms_levels,
            "source_context": context,
            "requirements": [
                "Use only supplied source_context.",
                "Every question must include at least one source reference with source_chunk_id.",
                "MCQ answers must include four choices labeled A, B, C, D and correct_option.",
                "Open-ended questions must include rubric.criteria.",
            ],
        }

        response = await self.client.chat.completions.create(
            model=request.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt["system"]},
                {"role": "developer", "content": prompt["developer"]},
                {"role": "user", "content": json.dumps(user_payload, default=str)},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise QuestionGenerationError("OpenAI returned an empty generation response")
        try:
            return GeneratedQuestionBatch.model_validate_json(content)
        except ValidationError as exc:
            raise QuestionGenerationError(f"Generated question JSON failed schema validation: {exc}") from exc

    def audit_request(
        self,
        topic: Topic,
        chunks: list[SourceChunk],
        request: QuestionGenerateRequest,
    ) -> dict:
        return {
            "topic_id": str(topic.id),
            "source_chunk_ids": [str(chunk.id) for chunk in chunks],
            "question_type": request.question_type,
            "count": request.count,
            "difficulty_target": request.difficulty_target,
            "model": request.model,
            "prompt_version": request.prompt_version,
        }

    def _format_context(self, chunks: list[SourceChunk]) -> list[dict]:
        return [
            {
                "source_chunk_id": str(chunk.id),
                "source_id": str(chunk.source_id),
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
            }
            for chunk in chunks
        ]

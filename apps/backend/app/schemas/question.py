import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.question import QuestionStatus, QuestionType


class GeneratedQuestionItem(BaseModel):
    type: QuestionType
    stem: str = Field(min_length=20)
    answer: dict
    rubric: dict = Field(default_factory=dict)
    blooms_level: str | None = None
    difficulty: float = Field(ge=-4.0, le=4.0)
    discrimination: float = Field(default=1.0, ge=0.1, le=3.0)
    source_references: list[dict] = Field(default_factory=list)


class QuestionGenerateRequest(BaseModel):
    topic_id: uuid.UUID
    question_type: QuestionType = QuestionType.mcq
    count: int = Field(default=3, ge=1, le=10)
    source_chunk_ids: list[uuid.UUID] = Field(default_factory=list)
    blooms_levels: list[str] = Field(default_factory=list)
    difficulty_target: float = Field(default=0.0, ge=-4.0, le=4.0)
    model: str = "gpt-4.1-mini"
    prompt_version: str = "2026-05-21.1"


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    subtopic_id: uuid.UUID | None
    learning_objective_id: uuid.UUID | None
    type: QuestionType
    status: QuestionStatus
    stem: str
    answer: dict
    rubric: dict
    blooms_level: str | None
    difficulty: Decimal
    discrimination: Decimal
    source_references: list[dict]
    canonical_fingerprint: str
    generation_metadata: dict


class QuestionGenerateResponse(BaseModel):
    created: list[QuestionRead]
    rejected: list[dict]
    audit_log_id: uuid.UUID | None


class QuestionStatusUpdate(BaseModel):
    status: Literal["draft", "validating", "approved", "rejected"]


class QuestionCandidateValidation(BaseModel):
    passed: bool
    confidence: float
    checks: dict
    notes: str | None = None

import uuid
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class QuestionType(StrEnum):
    mcq = "mcq"
    numeric = "numeric"
    open_ended = "open_ended"
    diagram = "diagram"


class QuestionStatus(StrEnum):
    draft = "draft"
    validating = "validating"
    approved = "approved"
    rejected = "rejected"


class Question(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "questions"

    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    subtopic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subtopics.id"))
    learning_objective_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("learning_objectives.id")
    )
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType, name="question_type"), nullable=False)
    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus, name="question_status"), nullable=False, default=QuestionStatus.draft
    )
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[dict] = mapped_column(JSONB, nullable=False)
    rubric: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    blooms_level: Mapped[str | None] = mapped_column(String(40))
    difficulty: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    discrimination: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=1.0)
    source_references: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    canonical_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    generation_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        UniqueConstraint("canonical_fingerprint", name="uq_questions_canonical_fingerprint"),
        Index("ix_questions_topic_difficulty", "topic_id", "difficulty"),
        Index("ix_questions_status", "status"),
    )


class QuestionEmbedding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "question_embeddings"

    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(120), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (UniqueConstraint("question_id", "embedding_model", name="uq_question_embedding"),)


class GenerationAuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "generation_audit_logs"

    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id"))
    source_chunk_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("source_chunks.id"))
    prompt_name: Mapped[str] = mapped_column(String(120), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    request_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    response_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(40), nullable=False)


class ValidationLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "question_validation_logs"

    question_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("questions.id"))
    checks: Mapped[dict] = mapped_column(JSONB, nullable=False)
    passed: Mapped[bool] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text)

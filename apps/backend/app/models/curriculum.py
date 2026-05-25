import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin, UUIDPrimaryKeyMixin


class SourceStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class Subject(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subjects"

    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    curriculum: Mapped[str] = mapped_column(String(60), nullable=False, default="IB")


class Unit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "units"

    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    subject: Mapped[Subject] = relationship()

    __table_args__ = (UniqueConstraint("subject_id", "code", name="uq_units_subject_code"),)


class Chapter(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "chapters"

    unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("units.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    unit: Mapped[Unit] = relationship()

    __table_args__ = (UniqueConstraint("unit_id", "code", name="uq_chapters_unit_code"),)


class Topic(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "topics"

    chapter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chapters.id"))
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    difficulty_weight: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=1.0)
    ib_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    formulas: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    misconception_tags: Mapped[list[str]] = mapped_column(ARRAY(String(80)), nullable=False, default=list)
    mastery_threshold: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=0.8)

    chapter: Mapped[Chapter | None] = relationship()

    __table_args__ = (
        UniqueConstraint("chapter_id", "code", name="uq_topics_chapter_code"),
        Index("ix_topics_code", "code"),
    )


class Subtopic(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subtopics"

    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    topic: Mapped[Topic] = relationship()

    __table_args__ = (UniqueConstraint("topic_id", "code", name="uq_subtopics_topic_code"),)


class LearningObjective(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "learning_objectives"

    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    subtopic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subtopics.id"))
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    blooms_level: Mapped[str | None] = mapped_column(String(40))

    topic: Mapped[Topic] = relationship()
    subtopic: Mapped[Subtopic | None] = relationship()

    __table_args__ = (UniqueConstraint("topic_id", "code", name="uq_learning_objectives_topic_code"),)


class TopicPrerequisite(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "topic_prerequisites"

    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    prerequisite_topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "topic_id", "prerequisite_topic_id", name="uq_topic_prerequisite_relation"
        ),
    )


class CurriculumSource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "curriculum_sources"

    subject_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subjects.id"))
    filename: Mapped[str] = mapped_column(String(260), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus, name="source_status"), nullable=False, default=SourceStatus.uploaded
    )
    extracted_text_hash: Mapped[str | None] = mapped_column(String(128))
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SourceChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "source_chunks"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("curriculum_sources.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, nullable=False)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id"))
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    source: Mapped[CurriculumSource] = relationship()
    topic: Mapped[Topic | None] = relationship()

    __table_args__ = (
        UniqueConstraint("source_id", "chunk_index", name="uq_source_chunks_source_index"),
        Index("ix_source_chunks_source_id", "source_id"),
    )

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    curriculum: str = "IB"


class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    curriculum: str


class TopicCreate(BaseModel):
    code: str
    title: str
    chapter_id: uuid.UUID | None = None
    description: str | None = None
    difficulty_weight: float = 1.0
    ib_metadata: dict = Field(default_factory=dict)
    formulas: list[str] = Field(default_factory=list)
    misconception_tags: list[str] = Field(default_factory=list)
    mastery_threshold: float = 0.8


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chapter_id: uuid.UUID | None
    code: str
    title: str
    description: str | None
    difficulty_weight: float
    ib_metadata: dict
    formulas: list[str]
    misconception_tags: list[str]
    mastery_threshold: float


class TopicPrerequisiteRead(BaseModel):
    topic_id: uuid.UUID
    prerequisites: list[TopicRead]


class CurriculumSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subject_id: uuid.UUID | None
    filename: str
    content_type: str
    storage_key: str
    version: int
    status: str
    metadata_json: dict
    processed_at: datetime | None


class SourceChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: uuid.UUID
    chunk_index: int
    text: str
    token_estimate: int
    topic_id: uuid.UUID | None
    metadata_json: dict


class IngestionResult(BaseModel):
    source: CurriculumSourceRead
    chunks_created: int
    queued_question_generation: bool


class BulkIngestionResult(BaseModel):
    results: list[IngestionResult]

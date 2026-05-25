import uuid

from pydantic import BaseModel


class KnowledgeBaseMapRequest(BaseModel):
    subject_id: uuid.UUID | None = None


class KnowledgeBaseMapResponse(BaseModel):
    subjects_processed: int
    topics_created: int
    chunks_mapped: int
    chunks_unmapped: int
    by_subject: dict[str, dict[str, int]]

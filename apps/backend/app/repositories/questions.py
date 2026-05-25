import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.curriculum import SourceChunk, Topic
from app.models.question import (
    GenerationAuditLog,
    Question,
    QuestionEmbedding,
    QuestionStatus,
    ValidationLog,
)


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_topic(self, topic_id: uuid.UUID) -> Topic | None:
        return await self.session.get(Topic, topic_id)

    async def get_source_chunks(
        self,
        topic_id: uuid.UUID,
        source_chunk_ids: list[uuid.UUID],
        limit: int = 8,
    ) -> list[SourceChunk]:
        statement = select(SourceChunk)
        if source_chunk_ids:
            statement = statement.where(SourceChunk.id.in_(source_chunk_ids))
        else:
            statement = statement.where(SourceChunk.topic_id == topic_id).limit(limit)
        result = await self.session.execute(statement.order_by(SourceChunk.chunk_index))
        return list(result.scalars())

    async def list_questions(
        self,
        status: QuestionStatus | None = None,
        topic_id: uuid.UUID | None = None,
        limit: int = 100,
    ) -> list[Question]:
        statement = select(Question)
        if status is not None:
            statement = statement.where(Question.status == status)
        if topic_id is not None:
            statement = statement.where(Question.topic_id == topic_id)
        result = await self.session.execute(
            statement.order_by(Question.created_at.desc()).limit(limit)
        )
        return list(result.scalars())

    async def get_question(self, question_id: uuid.UUID) -> Question | None:
        return await self.session.get(Question, question_id)

    async def find_by_fingerprint(self, fingerprint: str) -> Question | None:
        result = await self.session.execute(
            select(Question).where(Question.canonical_fingerprint == fingerprint)
        )
        return result.scalar_one_or_none()

    async def list_embeddings(self, model: str) -> list[QuestionEmbedding]:
        result = await self.session.execute(
            select(QuestionEmbedding).where(QuestionEmbedding.embedding_model == model)
        )
        return list(result.scalars())

    async def create_question(self, question: Question) -> Question:
        self.session.add(question)
        await self.session.flush()
        return question

    async def create_embedding(self, embedding: QuestionEmbedding) -> QuestionEmbedding:
        self.session.add(embedding)
        await self.session.flush()
        return embedding

    async def create_audit_log(self, audit_log: GenerationAuditLog) -> GenerationAuditLog:
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log

    async def create_validation_log(self, validation_log: ValidationLog) -> ValidationLog:
        self.session.add(validation_log)
        await self.session.flush()
        return validation_log

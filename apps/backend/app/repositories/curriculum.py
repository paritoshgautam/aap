import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.curriculum import (
    CurriculumSource,
    SourceChunk,
    SourceStatus,
    Subject,
    Topic,
    TopicPrerequisite,
)
from app.schemas.curriculum import SubjectCreate, TopicCreate


class CurriculumRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_subject(self, payload: SubjectCreate) -> Subject:
        subject = Subject(**payload.model_dump())
        self.session.add(subject)
        await self.session.flush()
        return subject

    async def get_subject(self, subject_id: uuid.UUID) -> Subject | None:
        return await self.session.get(Subject, subject_id)

    async def get_subject_by_code(self, code: str) -> Subject | None:
        result = await self.session.execute(select(Subject).where(Subject.code == code))
        return result.scalar_one_or_none()

    async def list_subjects(self) -> list[Subject]:
        result = await self.session.execute(select(Subject).order_by(Subject.name))
        return list(result.scalars())

    async def create_topic(self, payload: TopicCreate) -> Topic:
        topic = Topic(**payload.model_dump())
        self.session.add(topic)
        await self.session.flush()
        return topic

    async def list_topics(self) -> list[Topic]:
        result = await self.session.execute(select(Topic).order_by(Topic.code, Topic.title))
        return list(result.scalars())

    async def get_topic(self, topic_id: uuid.UUID) -> Topic | None:
        return await self.session.get(Topic, topic_id)

    async def add_prerequisite(
        self, topic_id: uuid.UUID, prerequisite_topic_id: uuid.UUID
    ) -> TopicPrerequisite:
        relation = TopicPrerequisite(
            topic_id=topic_id, prerequisite_topic_id=prerequisite_topic_id
        )
        self.session.add(relation)
        await self.session.flush()
        return relation

    async def list_prerequisites(self, topic_id: uuid.UUID) -> list[Topic]:
        result = await self.session.execute(
            select(Topic)
            .join(TopicPrerequisite, TopicPrerequisite.prerequisite_topic_id == Topic.id)
            .where(TopicPrerequisite.topic_id == topic_id)
            .order_by(Topic.code)
        )
        return list(result.scalars())

    async def create_source(self, source: CurriculumSource) -> CurriculumSource:
        self.session.add(source)
        await self.session.flush()
        return source

    async def get_source(self, source_id: uuid.UUID) -> CurriculumSource | None:
        return await self.session.get(CurriculumSource, source_id)

    async def create_chunks(self, chunks: list[SourceChunk]) -> list[SourceChunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks

    async def list_sources(
        self,
        subject_id: uuid.UUID | None = None,
        status: SourceStatus | None = None,
        limit: int = 100,
    ) -> list[CurriculumSource]:
        statement = select(CurriculumSource)
        if subject_id is not None:
            statement = statement.where(CurriculumSource.subject_id == subject_id)
        if status is not None:
            statement = statement.where(CurriculumSource.status == status)
        result = await self.session.execute(
            statement.order_by(CurriculumSource.created_at.desc()).limit(limit)
        )
        return list(result.scalars())

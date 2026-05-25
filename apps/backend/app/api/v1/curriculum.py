import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUserDep, SessionDep
from app.repositories.curriculum import CurriculumRepository
from app.schemas.curriculum import (
    SubjectCreate,
    SubjectRead,
    TopicCreate,
    TopicPrerequisiteRead,
    TopicRead,
)

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.post("/subjects", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
async def create_subject(
    payload: SubjectCreate, session: SessionDep, _admin: AdminUserDep
) -> SubjectRead:
    repository = CurriculumRepository(session)
    subject = await repository.create_subject(payload)
    await session.commit()
    return SubjectRead.model_validate(subject)


@router.get("/subjects", response_model=list[SubjectRead])
async def list_subjects(session: SessionDep) -> list[SubjectRead]:
    subjects = await CurriculumRepository(session).list_subjects()
    return [SubjectRead.model_validate(subject) for subject in subjects]


@router.post("/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
async def create_topic(payload: TopicCreate, session: SessionDep, _admin: AdminUserDep) -> TopicRead:
    repository = CurriculumRepository(session)
    topic = await repository.create_topic(payload)
    await session.commit()
    return TopicRead.model_validate(topic)


@router.get("/topics", response_model=list[TopicRead])
async def list_topics(session: SessionDep) -> list[TopicRead]:
    topics = await CurriculumRepository(session).list_topics()
    return [TopicRead.model_validate(topic) for topic in topics]


@router.post("/topics/{topic_id}/prerequisites/{prerequisite_topic_id}", status_code=204)
async def add_prerequisite(
    topic_id: uuid.UUID,
    prerequisite_topic_id: uuid.UUID,
    session: SessionDep,
    _admin: AdminUserDep,
) -> None:
    repository = CurriculumRepository(session)
    if await repository.get_topic(topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    if await repository.get_topic(prerequisite_topic_id) is None:
        raise HTTPException(status_code=404, detail="Prerequisite topic not found")
    await repository.add_prerequisite(topic_id, prerequisite_topic_id)
    await session.commit()


@router.get("/topics/{topic_id}/prerequisites", response_model=TopicPrerequisiteRead)
async def list_prerequisites(topic_id: uuid.UUID, session: SessionDep) -> TopicPrerequisiteRead:
    repository = CurriculumRepository(session)
    if await repository.get_topic(topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    prerequisites = await repository.list_prerequisites(topic_id)
    return TopicPrerequisiteRead(
        topic_id=topic_id,
        prerequisites=[TopicRead.model_validate(topic) for topic in prerequisites],
    )

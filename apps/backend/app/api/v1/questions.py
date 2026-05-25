import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminUserDep, SessionDep
from app.core.config import get_settings
from app.models.question import QuestionStatus
from app.repositories.questions import QuestionRepository
from app.schemas.question import (
    QuestionGenerateRequest,
    QuestionGenerateResponse,
    QuestionRead,
    QuestionStatusUpdate,
)
from app.services.questions.generator import QuestionGenerationError
from app.services.questions.pipeline import QuestionGenerationPipeline

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=list[QuestionRead])
async def list_questions(
    session: SessionDep,
    status_filter: QuestionStatus | None = Query(default=None, alias="status"),
    topic_id: uuid.UUID | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[QuestionRead]:
    questions = await QuestionRepository(session).list_questions(
        status=status_filter,
        topic_id=topic_id,
        limit=limit,
    )
    return [QuestionRead.model_validate(question) for question in questions]


@router.post("/generate", response_model=QuestionGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_questions(
    payload: QuestionGenerateRequest,
    session: SessionDep,
    _admin: AdminUserDep,
) -> QuestionGenerateResponse:
    pipeline = QuestionGenerationPipeline(get_settings(), session)
    try:
        response = await pipeline.run(payload)
        await session.commit()
        return response
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except QuestionGenerationError as exc:
        await session.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.patch("/{question_id}/status", response_model=QuestionRead)
async def update_question_status(
    question_id: uuid.UUID,
    payload: QuestionStatusUpdate,
    session: SessionDep,
    _admin: AdminUserDep,
) -> QuestionRead:
    repository = QuestionRepository(session)
    question = await repository.get_question(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    question.status = QuestionStatus(payload.status)
    await session.commit()
    return QuestionRead.model_validate(question)

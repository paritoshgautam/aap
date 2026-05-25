import uuid

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from app.api.deps import AdminUserDep, SessionDep
from app.core.config import get_settings
from app.models.curriculum import SourceStatus
from app.repositories.curriculum import CurriculumRepository
from app.schemas.curriculum import BulkIngestionResult, CurriculumSourceRead, IngestionResult
from app.services.ingestion.extractors import UnsupportedUploadTypeError
from app.services.ingestion.pipeline import IngestionPipeline

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/sources", response_model=BulkIngestionResult, status_code=status.HTTP_201_CREATED)
async def upload_curriculum_source(
    session: SessionDep,
    _admin: AdminUserDep,
    files: list[UploadFile] = File(...),
    subject_id: uuid.UUID | None = Form(default=None),
    topic_id: uuid.UUID | None = Form(default=None),
    curriculum: str = Form(default="IB"),
    level: str | None = Form(default=None),
    chunk_size: int | None = Form(default=None),
    chunk_overlap: int | None = Form(default=None),
) -> BulkIngestionResult:
    settings = get_settings()
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")
    for file in files:
        content_length = file.size or 0
        if content_length > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"{file.filename or 'Upload'} exceeds configured size limit",
            )

    pipeline = IngestionPipeline(settings, session)
    results: list[IngestionResult] = []
    try:
        for file in files:
            source, chunks = await pipeline.ingest(
                file,
                subject_id,
                topic_id=topic_id,
                metadata={
                    "curriculum": curriculum,
                    "level": level,
                    "topic_id": str(topic_id) if topic_id else None,
                },
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            results.append(
                IngestionResult(
                    source=source,
                    chunks_created=len(chunks),
                    queued_question_generation=bool(chunks),
                )
            )
        await session.commit()
    except UnsupportedUploadTypeError as exc:
        await session.rollback()
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    return BulkIngestionResult(results=results)


@router.get("/sources", response_model=list[CurriculumSourceRead])
async def list_curriculum_sources(
    session: SessionDep,
    _admin: AdminUserDep,
    subject_id: uuid.UUID | None = None,
    status_filter: SourceStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[CurriculumSourceRead]:
    sources = await CurriculumRepository(session).list_sources(
        subject_id=subject_id,
        status=status_filter,
        limit=limit,
    )
    return [CurriculumSourceRead.model_validate(source) for source in sources]

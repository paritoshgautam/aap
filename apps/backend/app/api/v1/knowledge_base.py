from fastapi import APIRouter

from app.api.deps import AdminUserDep, SessionDep
from app.schemas.knowledge_base import KnowledgeBaseMapRequest, KnowledgeBaseMapResponse
from app.services.knowledge_graph.kb_mapping import KnowledgeBaseMapper

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])


@router.post("/map", response_model=KnowledgeBaseMapResponse)
async def map_knowledge_base(
    payload: KnowledgeBaseMapRequest,
    session: SessionDep,
    _admin: AdminUserDep,
) -> KnowledgeBaseMapResponse:
    result = await KnowledgeBaseMapper(session).map_sources(payload.subject_id)
    await session.commit()
    return KnowledgeBaseMapResponse(
        subjects_processed=result.subjects_processed,
        topics_created=result.topics_created,
        chunks_mapped=result.chunks_mapped,
        chunks_unmapped=result.chunks_unmapped,
        by_subject=result.by_subject,
    )

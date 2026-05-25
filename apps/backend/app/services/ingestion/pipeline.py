import hashlib
import uuid
from datetime import UTC, datetime

import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.curriculum import CurriculumSource, SourceChunk, SourceStatus
from app.repositories.curriculum import CurriculumRepository
from app.services.ingestion.chunker import TextChunker
from app.services.ingestion.extractors import TextExtractor
from app.services.ingestion.source_type import detect_source_type
from app.services.knowledge_graph.topic_detection import TopicDetector
from app.services.storage import LocalObjectStorage

logger = structlog.get_logger(__name__)


class IngestionPipeline:
    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self.settings = settings
        self.repository = CurriculumRepository(session)
        self.storage = LocalObjectStorage(settings)
        self.extractor = TextExtractor()
        self.detector = TopicDetector()

    async def ingest(
        self,
        upload: UploadFile,
        subject_id: uuid.UUID | None,
        topic_id: uuid.UUID | None = None,
        metadata: dict | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> tuple[CurriculumSource, list[SourceChunk]]:
        key, path = await self.storage.save_upload(upload)
        source = await self.repository.create_source(
            CurriculumSource(
                subject_id=subject_id,
                filename=upload.filename or path.name,
                content_type=upload.content_type or "application/octet-stream",
                storage_key=key,
                status=SourceStatus.processing,
                metadata_json={"pipeline_version": "2026-05-21.1", **(metadata or {})},
            )
        )

        try:
            text = self.extractor.extract(path, source.content_type)
            text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            source.metadata_json = {
                **source.metadata_json,
                "source_type": source.metadata_json.get("source_type")
                or detect_source_type(source.filename, text),
                "source_type_detection": "filename_text_rules_v1",
            }
            chunker = TextChunker(
                chunk_size=chunk_size or self.settings.default_chunk_size,
                overlap=chunk_overlap or self.settings.default_chunk_overlap,
            )
            text_chunks = chunker.chunk(text)
            topics = await self.repository.list_topics()

            chunks = [
                SourceChunk(
                    source_id=source.id,
                    chunk_index=chunk.index,
                    text=chunk.text,
                    token_estimate=chunk.token_estimate,
                    topic_id=topic_id or self.detector.detect_topic_id(chunk.text, topics),
                    metadata_json={"chunker": "paragraph_boundary_v1"},
                )
                for chunk in text_chunks
            ]
            await self.repository.create_chunks(chunks)

            source.status = SourceStatus.processed
            source.extracted_text_hash = text_hash
            source.processed_at = datetime.now(UTC)
            source.metadata_json = {
                **source.metadata_json,
                "chunk_count": len(chunks),
                "queued_question_generation": bool(chunks),
            }
            logger.info("curriculum_source_ingested", source_id=str(source.id), chunks=len(chunks))
            return source, chunks
        except Exception as exc:
            source.status = SourceStatus.failed
            source.metadata_json = {**source.metadata_json, "error": str(exc)}
            logger.exception("curriculum_source_ingestion_failed", source_id=str(source.id))
            raise

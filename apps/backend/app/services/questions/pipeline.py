import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.question import GenerationAuditLog, Question, QuestionEmbedding, QuestionStatus, ValidationLog
from app.repositories.questions import QuestionRepository
from app.schemas.question import QuestionGenerateRequest, QuestionGenerateResponse, QuestionRead
from app.services.questions.embeddings import EmbeddingService, cosine_similarity
from app.services.questions.fingerprinting import StructuralFingerprinter
from app.services.questions.generator import OpenAIQuestionGenerator
from app.services.questions.validation import QuestionValidator


class QuestionGenerationPipeline:
    semantic_duplicate_threshold = 0.92

    def __init__(self, settings: Settings, session: AsyncSession) -> None:
        self.repository = QuestionRepository(session)
        self.generator = OpenAIQuestionGenerator(settings)
        self.embeddings = EmbeddingService(settings.openai_api_key)
        self.fingerprinter = StructuralFingerprinter()
        self.validator = QuestionValidator()

    async def run(self, request: QuestionGenerateRequest) -> QuestionGenerateResponse:
        topic = await self.repository.get_topic(request.topic_id)
        if topic is None:
            raise ValueError("Topic not found")

        chunks = await self.repository.get_source_chunks(request.topic_id, request.source_chunk_ids)
        if not chunks:
            raise ValueError("No source chunks available for generation")

        audit_log = await self.repository.create_audit_log(
            GenerationAuditLog(
                topic_id=topic.id,
                source_chunk_id=chunks[0].id,
                prompt_name="question_generation",
                prompt_version=request.prompt_version,
                model=request.model,
                request_json=self.generator.audit_request(topic, chunks, request),
                status="started",
            )
        )

        created: list[Question] = []
        rejected: list[dict] = []

        try:
            batch = await self.generator.generate(topic, chunks, request)
            audit_log.response_json = batch.model_dump(mode="json")
            audit_log.status = "generated"
        except Exception as exc:
            audit_log.status = "failed"
            audit_log.response_json = {"error": str(exc)}
            raise

        for candidate in batch.questions:
            validation = self.validator.validate(candidate)
            fingerprint = self.fingerprinter.fingerprint(candidate.stem, candidate.answer)
            existing = await self.repository.find_by_fingerprint(fingerprint)

            rejection_reason = None
            embedding = await self.embeddings.embed(candidate.stem)
            if existing is not None:
                rejection_reason = "structural_duplicate"
            elif embedding is not None:
                semantic_duplicate = await self._find_semantic_duplicate(embedding)
                if semantic_duplicate is not None:
                    rejection_reason = "semantic_duplicate"
            if not validation.passed:
                rejection_reason = "validation_failed"

            if rejection_reason:
                rejected.append(
                    {
                        "reason": rejection_reason,
                        "stem": candidate.stem,
                        "validation": validation.model_dump(),
                    }
                )
                await self.repository.create_validation_log(
                    ValidationLog(
                        question_id=None,
                        checks=validation.checks,
                        passed=False,
                        confidence=validation.confidence,
                        notes=validation.notes or rejection_reason,
                    )
                )
                continue

            question = await self.repository.create_question(
                Question(
                    topic_id=topic.id,
                    type=candidate.type,
                    status=QuestionStatus.draft,
                    stem=candidate.stem,
                    answer=candidate.answer,
                    rubric=candidate.rubric,
                    blooms_level=candidate.blooms_level,
                    difficulty=candidate.difficulty,
                    discrimination=candidate.discrimination,
                    source_references=candidate.source_references,
                    canonical_fingerprint=fingerprint,
                    generation_metadata={
                        "model": request.model,
                        "prompt_version": request.prompt_version,
                        "audit_log_id": str(audit_log.id),
                    },
                )
            )
            await self.repository.create_validation_log(
                ValidationLog(
                    question_id=question.id,
                    checks=validation.checks,
                    passed=True,
                    confidence=validation.confidence,
                    notes=validation.notes,
                )
            )
            if embedding is not None:
                await self.repository.create_embedding(
                    QuestionEmbedding(
                        question_id=question.id,
                        embedding_model=self.embeddings.model,
                        embedding=embedding,
                    )
                )
            created.append(question)

        audit_log.status = "persisted"
        return QuestionGenerateResponse(
            created=[QuestionRead.model_validate(question) for question in created],
            rejected=rejected,
            audit_log_id=audit_log.id,
        )

    async def _find_semantic_duplicate(self, embedding: list[float]) -> uuid.UUID | None:
        existing_embeddings = await self.repository.list_embeddings(self.embeddings.model)
        for existing in existing_embeddings:
            if cosine_similarity(embedding, existing.embedding) >= self.semantic_duplicate_threshold:
                return existing.question_id
        return None

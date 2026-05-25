import re
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.curriculum import CurriculumSource, SourceChunk, Subject, Topic
from app.services.knowledge_graph.topic_taxonomy import TopicDefinition, topics_for_subject


@dataclass(frozen=True)
class KnowledgeBaseMappingResult:
    subjects_processed: int
    topics_created: int
    chunks_mapped: int
    chunks_unmapped: int
    by_subject: dict[str, dict[str, int]]


class KnowledgeBaseMapper:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def map_sources(self, subject_id: uuid.UUID | None = None) -> KnowledgeBaseMappingResult:
        subjects = await self._subjects(subject_id)
        topics_created = 0
        chunks_mapped = 0
        chunks_unmapped = 0
        by_subject: dict[str, dict[str, int]] = {}

        for subject in subjects:
            definitions = topics_for_subject(subject.name)
            if not definitions:
                continue
            topic_map, created_count = await self._ensure_topics(subject, definitions)
            topics_created += created_count

            subject_counter: Counter[str] = Counter()
            sources = await self._sources_for_subject(subject.id)
            for source in sources:
                chunks = await self._chunks_for_source(source.id)
                source_topic = self._infer_source_topic(source, chunks, definitions)
                for chunk in chunks:
                    definition = self._infer_chunk_topic(source, chunk, definitions) or source_topic
                    if definition is None:
                        chunks_unmapped += 1
                        continue
                    topic = topic_map[definition.code]
                    chunk.topic_id = topic.id
                    chunk.metadata_json = {
                        **chunk.metadata_json,
                        "topic_mapping": {
                            "method": "keyword_taxonomy_v1",
                            "topic_code": definition.code,
                        },
                    }
                    subject_counter[definition.title] += 1
                    chunks_mapped += 1

                if source_topic is not None:
                    source.metadata_json = {
                        **source.metadata_json,
                        "inferred_topic_code": source_topic.code,
                        "inferred_topic_title": source_topic.title,
                    }
                source.metadata_json = {
                    **source.metadata_json,
                    "topic_mapping_version": "keyword_taxonomy_v1",
                }

            by_subject[subject.name] = dict(subject_counter)

        await self.session.flush()
        return KnowledgeBaseMappingResult(
            subjects_processed=len(subjects),
            topics_created=topics_created,
            chunks_mapped=chunks_mapped,
            chunks_unmapped=chunks_unmapped,
            by_subject=by_subject,
        )

    async def _subjects(self, subject_id: uuid.UUID | None) -> list[Subject]:
        statement = select(Subject)
        if subject_id is not None:
            statement = statement.where(Subject.id == subject_id)
        result = await self.session.execute(statement.order_by(Subject.name))
        return list(result.scalars())

    async def _sources_for_subject(self, subject_id: uuid.UUID) -> list[CurriculumSource]:
        result = await self.session.execute(
            select(CurriculumSource)
            .where(CurriculumSource.subject_id == subject_id)
            .order_by(CurriculumSource.filename)
        )
        return list(result.scalars())

    async def _chunks_for_source(self, source_id: uuid.UUID) -> list[SourceChunk]:
        result = await self.session.execute(
            select(SourceChunk)
            .where(SourceChunk.source_id == source_id)
            .order_by(SourceChunk.chunk_index)
        )
        return list(result.scalars())

    async def _ensure_topics(
        self, subject: Subject, definitions: tuple[TopicDefinition, ...]
    ) -> tuple[dict[str, Topic], int]:
        result = await self.session.execute(select(Topic))
        existing = [
            topic
            for topic in result.scalars()
            if topic.ib_metadata.get("subject_id") == str(subject.id)
        ]
        existing_by_code = {topic.code: topic for topic in existing}
        created = 0
        for definition in definitions:
            if definition.code in existing_by_code:
                continue
            topic = Topic(
                code=definition.code,
                title=definition.title,
                description=f"Auto-created {subject.name} topic from uploaded knowledge base.",
                ib_metadata={
                    "subject_id": str(subject.id),
                    "subject": subject.name,
                    "curriculum": subject.curriculum,
                    "created_by": "kb_mapper",
                },
                misconception_tags=[],
                formulas=[],
            )
            self.session.add(topic)
            await self.session.flush()
            existing_by_code[topic.code] = topic
            created += 1
        return existing_by_code, created

    def _infer_source_topic(
        self,
        source: CurriculumSource,
        chunks: list[SourceChunk],
        definitions: tuple[TopicDefinition, ...],
    ) -> TopicDefinition | None:
        filename_text = self._filename_signal(source.filename)
        sampled_text = " ".join(chunk.text[:800] for chunk in chunks[:5])
        return self._best_topic(f"{filename_text} {sampled_text}", definitions, minimum_score=2)

    def _infer_chunk_topic(
        self,
        source: CurriculumSource,
        chunk: SourceChunk,
        definitions: tuple[TopicDefinition, ...],
    ) -> TopicDefinition | None:
        filename_text = self._filename_signal(source.filename)
        return self._best_topic(f"{filename_text} {chunk.text}", definitions, minimum_score=1)

    def _best_topic(
        self,
        text: str,
        definitions: tuple[TopicDefinition, ...],
        minimum_score: int,
    ) -> TopicDefinition | None:
        haystack = text.lower()
        scores: defaultdict[TopicDefinition, int] = defaultdict(int)
        for definition in definitions:
            for keyword in definition.keywords:
                pattern = rf"\b{re.escape(keyword.lower())}\b"
                matches = len(re.findall(pattern, haystack))
                if matches:
                    scores[definition] += matches * max(1, len(keyword.split()))
        if not scores:
            return None
        definition, score = max(scores.items(), key=lambda item: item[1])
        return definition if score >= minimum_score else None

    def _filename_signal(self, filename: str) -> str:
        stem = Path(filename).stem.lower()
        stem = re.sub(r"ch(\d+)", r" chapter \1 ", stem)
        stem = re.sub(r"[_\-()]+", " ", stem)
        return stem

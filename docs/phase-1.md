# Phase 1 Build Notes

## Architecture Decisions

- Monorepo with `apps/backend`, `apps/frontend`, `infra`, and `scripts`.
- Backend uses FastAPI, Python 3.12, SQLAlchemy async sessions, Alembic migrations, and structured JSON logging.
- Database schema is normalized around curriculum graph entities, question lifecycle, exam sessions, attempts, exposure memory, and analytics snapshots.
- Upload processing is synchronous for the MVP API path, with a Dramatiq worker boundary already present for question generation and heavier AI jobs.
- Object storage is abstracted behind `LocalObjectStorage`; S3-compatible storage can replace the implementation without changing ingestion API contracts.
- Prompts live in `apps/backend/app/prompts` with name/version metadata for auditability.

## Folder Structure

```text
apps/backend/app/api/v1        REST API routers
apps/backend/app/core          settings and logging
apps/backend/app/db            async engine/session
apps/backend/app/models        SQLAlchemy domain models
apps/backend/app/repositories  database access boundaries
apps/backend/app/schemas       Pydantic API contracts
apps/backend/app/services      ingestion, storage, topic mapping
apps/backend/alembic           PostgreSQL migrations
apps/frontend/app              Next.js App Router pages
apps/frontend/components       Shared UI components
infra/postgres                 local database bootstrap
```

## Migration

Initial migration:

```bash
cd apps/backend
alembic upgrade head
```

It creates:

- `users`, `students`
- `subjects`, `units`, `chapters`, `topics`, `subtopics`, `learning_objectives`, `topic_prerequisites`
- `curriculum_sources`, `source_chunks`
- `questions`, `question_embeddings`, `generation_audit_logs`, `question_validation_logs`
- `exams`, `exam_sessions`, `question_attempts`
- `student_topic_mastery`, `analytics_snapshots`

## API Contracts

Base path: `/api/v1`

- `GET /health`
- `POST /curriculum/subjects`
- `GET /curriculum/subjects`
- `POST /curriculum/topics`
- `GET /curriculum/topics`
- `POST /curriculum/topics/{topic_id}/prerequisites/{prerequisite_topic_id}`
- `GET /curriculum/topics/{topic_id}/prerequisites`
- `POST /ingestion/sources`

`POST /ingestion/sources` accepts multipart form data:

- `file`: `.pdf`, `.docx`, `.txt`, or `.md`
- `subject_id`: optional UUID
- `chunk_size`: optional integer
- `chunk_overlap`: optional integer

It returns the persisted source, chunk count, and whether question generation should be queued.

## Next Steps

1. Add JWT auth, role dependencies, and upload rate limiting.
2. Move ingestion to worker execution for large sources and wire generation queue dispatch.
3. Replace heuristic topic detection with embedding-assisted retrieval and topic classification.
4. Implement question generation, validation, deduplication, and admin review APIs.
5. Implement adaptive session progression and exposure memory rules.

## Phase 2 Addendum

Question system endpoints:

- `GET /questions`
- `GET /questions?status=draft`
- `POST /questions/generate`
- `PATCH /questions/{question_id}/status`

`POST /questions/generate` requires a topic with ingested source chunks. The pipeline retrieves source
context, calls OpenAI for structured JSON, validates each candidate, checks structural fingerprints,
checks semantic similarity when embeddings are available, persists accepted drafts, and records audit
and validation logs.

## Phase 3 Addendum

Admin knowledge-base management now includes:

- `POST /auth/bootstrap-admin` to create the first local admin only when no admin exists.
- `POST /auth/login` to issue a JWT bearer token.
- Admin role guards for curriculum writes, ingestion uploads, question generation, and question status changes.
- `GET /ingestion/sources` for authenticated source review.
- `/login` frontend page for admin sign-in/bootstrap.
- `/upload` frontend page for subject creation, topic creation, tagged KB uploads, and source review.

Uploads can now include subject, topic, curriculum, level, and source type metadata. This supports
separate Chemistry and Physics knowledge bases while preserving a common IB curriculum ingestion flow.

# Adaptive Assessment Platform

Production-oriented MVP for IB Chemistry adaptive assessment.

## Phase 1 Scope

- FastAPI backend with async PostgreSQL access
- PostgreSQL schema with pgvector-ready embeddings
- Curriculum source ingestion MVP for PDF, DOCX, and text uploads
- Topic graph CRUD/traversal foundation
- Question generation queue/audit placeholders with typed boundaries
- Next.js App Router frontend shell for core product pages
- Docker Compose local environment for API, Postgres, Redis, worker, and frontend

## Monorepo

```text
apps/
  backend/      FastAPI service, database models, ingestion services
  frontend/     Next.js App Router UI
infra/
  postgres/     Database bootstrap scripts
scripts/        Local utility scripts
```

## Local Development

```bash
docker compose up --build
```

Backend API docs: http://localhost:8000/docs

Frontend: http://localhost:3000

## Architecture Decisions

- Backend is async-first with FastAPI, SQLAlchemy 2.0 async sessions, and repository-oriented service boundaries.
- PostgreSQL stores normalized curriculum graph entities and pgvector-compatible embeddings.
- Redis is available for cache/rate limiting and Dramatiq broker usage.
- Ingestion is versioned at the curriculum source level and records auditable pipeline events.
- AI prompts are externalized under `apps/backend/app/prompts` with prompt version fields in generation audit tables.

from fastapi import APIRouter

from app.api.v1 import auth, curriculum, health, ingestion, knowledge_base, questions

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(curriculum.router)
api_router.include_router(ingestion.router)
api_router.include_router(knowledge_base.router)
api_router.include_router(questions.router)

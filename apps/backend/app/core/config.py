from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env", ".env"),
        extra="ignore",
    )

    app_env: str = "local"
    app_name: str = "Adaptive Assessment API"
    database_url: str = "postgresql+asyncpg://adaptive:adaptive@localhost:5432/adaptive_assessment"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = Field(default="local-dev-change-me", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    openai_api_key: str | None = None
    storage_root: Path = Path("uploads")
    max_upload_mb: int = 50
    default_chunk_size: int = 1200
    default_chunk_overlap: int = 160
    embedding_dimensions: int = 1536


@lru_cache
def get_settings() -> Settings:
    return Settings()

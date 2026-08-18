import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SQL-Agent"
    log_level: str = "INFO"

    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    base_url: str = os.getenv("BASE_URL", "")
    model: str = os.getenv("MODEL", "")

    broker_uri: str = "redis://localhost:6379/0"
    backend_uri: str = "redis://localhost:6379/1"
    redis_url: str = "redis://localhost:6379/2"

    job_ttl_seconds: int = int(os.getenv("JOB_TTL_SECONDS", "86400"))
    redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "64"))
    celery_concurrency: int = int(os.getenv("CELERY_CONCURRENCY", "2"))
    uvicorn_workers: int = int(os.getenv("UVICORN_WORKERS", "4"))

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
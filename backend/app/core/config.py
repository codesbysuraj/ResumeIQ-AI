"""Application configuration loaded exclusively from environment variables."""
import os
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Type-safe settings with a required cloud PostgreSQL connection URL."""

    PROJECT_NAME: str = "ResumeIQ AI"
    PROJECT_DESCRIPTION: str = "Agentic NLP Resume Screening & Recruitment Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    DATABASE_URL: str

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    SPACY_MODEL: str = "en_core_web_sm"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    PROCESSED_DIR: str = str(BASE_DIR / "storage" / "processed")
    TEMP_DIR: str = str(BASE_DIR / "storage" / "temp")
    MAX_UPLOAD_SIZE_MB: int = 10

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Require a SQLAlchemy-compatible PostgreSQL URL from the environment."""
        url = value.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if not url.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must use the postgresql:// scheme.")
        return url

    @property
    def database_url(self) -> str:
        """Return the validated DATABASE_URL used by SQLAlchemy and Alembic."""
        return self.DATABASE_URL

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert the configured MB upload limit to bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    def ensure_directories(self) -> None:
        """Create required storage directories if they do not exist."""
        for directory in [self.UPLOAD_DIR, self.PROCESSED_DIR, self.TEMP_DIR]:
            os.makedirs(directory, exist_ok=True)

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
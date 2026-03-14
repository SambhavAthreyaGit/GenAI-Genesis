"""Environment-based configuration. Uses pydantic-settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Anthropic / LLM
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Storage
    storage_path: str = "storage"
    database_url: str = "sqlite:///./storage/projects.db"

    # Sandbox
    sandbox_image: str = "genai-genesis-sandbox:latest"
    sandbox_timeout_seconds: int = 120

    # API
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    def storage_dir(self) -> Path:
        return Path(self.storage_path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()

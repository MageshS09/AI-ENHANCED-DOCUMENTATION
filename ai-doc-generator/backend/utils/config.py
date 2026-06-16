"""Application configuration."""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Runtime settings sourced from environment variables."""

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    allowed_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    rate_limit_requests: int = 5
    rate_limit_window_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Parse comma-separated CORS origins from environment variables."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()

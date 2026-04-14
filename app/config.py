"""Configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # App
    app_name: str = "MyL Primer Bloque - Base de Datos"
    debug: bool = False

    # Database
    database_url: str = ""

    # Images (for proxy fallback)
    images_url: str = "https://api.myl.cl/static/cards"

    # Notion (contact form)
    notion_token: str = ""
    notion_feedback_db_id: str = "6bf46aba376b4256b655bb79295cda89"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

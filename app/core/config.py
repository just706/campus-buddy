"""Application configuration loaded from environment variables.

Uses pydantic-settings to parse .env and environment variables into a
typed Settings object available throughout the application.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables.

    All values have sensible defaults for development. Override via .env
    or environment variables in production.
    """

    # ===== Application =====
    APP_NAME: str = "CampusBuddy"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me"

    # ===== Database =====
    DATABASE_URL: str = "sqlite+aiosqlite:///./campus_buddy.db"

    # ===== JWT =====
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ===== LLM (Pydantic-AI) =====
    PDAI_BASE_URL: str = "https://api.openai.com/v1"
    PDAI_API_KEY: str = ""
    PDAI_MODEL: str = "gpt-4o-mini"

    # ===== Server =====
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # ===== CORS =====
    CORS_ORIGINS: list[str] = ["*"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()

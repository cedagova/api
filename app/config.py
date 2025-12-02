"""
Application configuration using Pydantic Settings.

This module loads environment variables from .env files based on the ENVIRONMENT variable.
Supports development (.env.dev) and production (.env.prod) configurations.
"""
import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: Literal["dev", "prod"] = "dev"
    debug: bool = False

    # Application
    app_name: str = "FastAPI Application"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 9000

    # Database (example - add your database config here)
    database_url: str = "sqlite:///./app.db"

    # Security (example - add your security config here)
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" for prod, "text" for dev

    # CORS
    cors_origins: str = "https://ui-xtcp.onrender.com"  # Comma-separated list of allowed origins

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).

    Loads environment-specific .env file based on ENVIRONMENT variable:
    - If ENVIRONMENT=dev, loads .env.dev
    - If ENVIRONMENT=prod, loads .env.prod
    - Falls back to .env if ENVIRONMENT is not set

    Environment variables take precedence over .env file values.
    """
    # Get environment from env var or default to dev
    environment = os.getenv("ENVIRONMENT", "dev").lower()

    # Determine which .env file to load
    env_file = f".env.{environment}" if environment in ["dev", "prod"] else ".env"

    # Check if the env file exists, otherwise fall back to .env
    if not os.path.exists(env_file):
        env_file = ".env" if os.path.exists(".env") else None

    # Load settings with the appropriate env file
    # pydantic-settings will also read from actual environment variables (which take precedence)
    settings = Settings(_env_file=env_file)

    # Override environment from the ENVIRONMENT env var
    settings.environment = environment

    return settings


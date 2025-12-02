"""
Logging configuration for the application.

Provides structured JSON logging for production and readable text logging for development.
"""
import logging
import sys
from typing import Optional

from pythonjsonlogger import jsonlogger

from app.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    Configure application logging based on environment.

    - Production: JSON structured logging (for log aggregation systems)
    - Development: Human-readable text logging
    """
    # Determine log format based on environment
    use_json = settings.log_format.lower() == "json" or settings.environment == "prod"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if use_json:
        # JSON formatter for production (structured logging)
        json_formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Text formatter for development (human-readable)
        text_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d]",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(text_formatter)

    root_logger.addHandler(console_handler)

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Log the logging configuration
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "environment": settings.environment,
            "log_level": settings.log_level,
            "log_format": "json" if use_json else "text",
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


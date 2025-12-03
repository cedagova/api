"""
Middleware for request/response logging and monitoring.
"""

import time
from typing import Callable

import sentry_sdk
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses with detailed information.

    Logs:
    - Request method, path, query parameters
    - Client IP and user agent
    - Request processing time
    - Response status code
    - Error details if any
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()

        # Extract request information
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request
        logger.info(
            "Incoming request",
            extra={
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "request_id": request.headers.get("x-request-id", "none"),
            },
        )

        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log successful response
            logger.info(
                "Request completed",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                    "client_ip": client_ip,
                },
            )

            # Add process time to response headers
            response.headers["X-Process-Time"] = str(round(process_time, 4))

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Capture exception to Sentry (if initialized)
            if sentry_sdk.Hub.current.client:
                try:
                    with sentry_sdk.push_scope() as scope:
                        scope.set_context(
                            "request",
                            {
                                "method": method,
                                "path": path,
                                "query_params": query_params,
                                "client_ip": client_ip,
                            },
                        )
                        sentry_sdk.capture_exception(e)
                except Exception as sentry_error:
                    logger.warning(f"Sentry reporting failed: {sentry_error}")

            # Log error
            logger.error(
                "Request failed",
                extra={
                    "method": method,
                    "path": path,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "process_time_ms": round(process_time * 1000, 2),
                    "client_ip": client_ip,
                },
                exc_info=True,
            )

            # Re-raise the exception
            raise

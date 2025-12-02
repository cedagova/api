from fastapi import FastAPI, Request
from app.api.v1.router import api_router
from app.config import get_settings
from app.logging_config import setup_logging, get_logger
from app.middleware import LoggingMiddleware

# Setup logging first
setup_logging()
logger = get_logger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="A simple FastAPI application",
    version=settings.app_version,
    debug=settings.debug,
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event():
    """Log application startup with detailed information."""
    logger.info(
        "Application started",
        extra={
            "event": "startup",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port,
            "log_level": settings.log_level,
            "log_format": settings.log_format,
        },
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info(
        "Application shutting down",
        extra={
            "event": "shutdown",
            "environment": settings.environment,
        },
    )


@app.get("/")
async def root(request: Request):
    """Root endpoint - welcome message."""
    logger.info(
        "Root endpoint accessed",
        extra={"client_ip": request.client.host if request.client else "unknown"},
    )
    return {"message": "Welcome to FastAPI"}


@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint with detailed status information."""
    logger.debug(
        "Health check requested",
        extra={
            "client_ip": request.client.host if request.client else "unknown",
            "environment": settings.environment,
        },
    )
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.app_version,
    }


@app.get("/test")
async def test_endpoint(request: Request):
    """Test endpoint for verification."""
    logger.info(
        "Test endpoint accessed",
        extra={
            "client_ip": request.client.host if request.client else "unknown",
            "endpoint": "/test",
        },
    )
    return {"success": True, "message": "Test endpoint is working correctly"}

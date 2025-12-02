from fastapi import APIRouter, Request, HTTPException

from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
async def throw_error(request: Request):
    """Endpoint that throws an error for testing purposes"""
    logger.info(
        "Error endpoint accessed",
        extra={
            "endpoint": "/errors",
            "method": "GET",
            "client_ip": request.client.host if request.client else "unknown",
        },
    )
    raise HTTPException(status_code=500, detail="This is a test error endpoint")


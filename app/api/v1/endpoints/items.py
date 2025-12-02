from fastapi import APIRouter, Request

from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
async def list_items(request: Request):
    """List all items"""
    logger.info(
        "Listing items",
        extra={
            "endpoint": "/items",
            "method": "GET",
            "client_ip": request.client.host if request.client else "unknown",
        },
    )
    items = []
    logger.debug(f"Returning {len(items)} items")
    return {"items": items}


@router.get("/{item_id}")
async def get_item(item_id: int, request: Request):
    """Get a specific item by ID"""
    logger.info(
        "Getting item",
        extra={
            "endpoint": "/items/{item_id}",
            "method": "GET",
            "item_id": item_id,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )
    item = {"item_id": item_id, "name": f"Item {item_id}"}
    logger.debug(f"Item retrieved: {item}")
    return item


@router.post("/")
async def create_item(item: dict, request: Request):
    """Create a new item"""
    logger.info(
        "Creating item",
        extra={
            "endpoint": "/items",
            "method": "POST",
            "item_data": item,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )
    created_item = {"message": "Item created", "item": item}
    logger.info(f"Item created successfully: {created_item}")
    return created_item


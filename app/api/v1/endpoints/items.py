from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_items():
    """List all items"""
    return {"items": []}


@router.get("/{item_id}")
async def get_item(item_id: int):
    """Get a specific item by ID"""
    return {"item_id": item_id, "name": f"Item {item_id}"}


@router.post("/")
async def create_item(item: dict):
    """Create a new item"""
    return {"message": "Item created", "item": item}


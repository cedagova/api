from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="FastAPI Application",
    description="A simple FastAPI application",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/test")
async def test_endpoint():
    return {"success": True, "message": "Test endpoint is working correctly"}


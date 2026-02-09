"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check if the API is running"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="QuickBooks Commerce Forecasting API"
    )


@router.get("/ready")
async def readiness_check():
    """Check if the API is ready to serve requests"""
    # Add checks for dependencies (DB, cache, model loaded, etc.)
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "api": "ok",
            "model": "loaded",
            "data": "available"
        }
    }

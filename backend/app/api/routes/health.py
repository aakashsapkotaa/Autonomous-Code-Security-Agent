"""
Health check endpoints
"""
from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SecureShift API"
    }

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness check endpoint"""
    # TODO: Add checks for database, redis, etc.
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }

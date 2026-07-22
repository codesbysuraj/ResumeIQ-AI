"""
Health check route.

Provides a lightweight liveness endpoint for monitoring tools,
load balancers, and deployment pipelines to confirm the backend
is running and correctly configured.
"""
from fastapi import APIRouter

from app.core.config import settings
from app.core.database import check_database_connection

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    tags=["Health"],
    response_description="Service status and metadata",
)
def health_check() -> dict:
    """
    Returns the current service status, database connection state, and metadata.
    """
    db_ok = check_database_connection()
    return {
        "status": "online" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


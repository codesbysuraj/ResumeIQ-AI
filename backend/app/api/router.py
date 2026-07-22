"""
API router — aggregates all route modules.

Every new route module is registered here with its URL prefix and tags.
This is the only file that knows about all available routes.
main.py mounts this router once under /api/v1.
"""
from fastapi import APIRouter

from app.api.routes import health, resume, job_description, matching

api_router = APIRouter()

# ── Health ─────────────────────────────────────────────────────────────────
api_router.include_router(health.router)
api_router.include_router(resume.router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(job_description.router, prefix="/jd", tags=["Job Descriptions"])
api_router.include_router(matching.router, prefix="/matching", tags=["Matching"])

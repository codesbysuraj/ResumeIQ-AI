"""
ResumeIQ AI — Application Entry Point.

This file is the uvicorn launch target.
All application logic lives in app/main.py.

Run:
    uvicorn main:app --reload            # development
    uvicorn main:app --host 0.0.0.0      # production (via Docker)
"""
import uvicorn

from app.main import create_app
from app.core.config import settings

# The ``app`` name is the uvicorn target: ``uvicorn main:app``
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

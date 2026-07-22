"""
ResumeIQ AI — FastAPI application factory.

This module owns the application lifecycle:
    - Lifespan context: startup logging, directory creation, shutdown
    - Middleware: CORS, request logging
    - Exception handlers: centralized, structured JSON errors
    - Router: all API routes mounted under /api/v1

Design:
    ``create_app()`` is a factory function instead of a module-level instance.
    This means tests can call ``create_app()`` to get a fresh, isolated instance
    without importing a shared global — making tests independent of each other.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import RequestLoggingMiddleware, get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages startup and shutdown tasks for the FastAPI application.

    Startup:
        1. Configure structured logging so all subsequent log calls are formatted.
        2. Ensure storage directories exist on disk.
        3. Initialize database tables.
        4. Log a confirmation message.

    Shutdown:
        1. Log a graceful shutdown message.
    """
    setup_logging()
    settings.ensure_directories()
    try:
        init_db()
    except Exception as e:
        logger.critical("Failed to initialize database on startup: %s", str(e))
    logger.info(
        "%s v%s starting — env=%s  debug=%s",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENV,
        settings.DEBUG,
    )
    yield
    logger.info("%s shut down gracefully.", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        A fully configured FastAPI instance ready to serve requests.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # ── Exception Handlers ─────────────────────────────────────────────
    # Must be registered before middleware so they can intercept errors
    # raised inside middleware stacks.
    register_exception_handlers(app)

    # ── CORS ───────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request Logging ────────────────────────────────────────────────
    # Raw ASGI middleware — avoids BaseHTTPMiddleware streaming issues.
    app.add_middleware(RequestLoggingMiddleware)

    # ── Root Endpoint ──────────────────────────────────────────────────
    @app.get("/", tags=["Root"], summary="API Root")
    def root() -> dict:
        """Returns API metadata and links to documentation."""
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health",
        }

    # ── API Routes ─────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

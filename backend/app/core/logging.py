"""
Structured logging configuration.

Provides:
    - setup_logging()            — initializes the root logger on startup
    - get_logger(name)           — returns a named logger for any module
    - RequestLoggingMiddleware   — ASGI middleware that logs every HTTP request

In development (LOG_FORMAT=text): human-readable colored output.
In production  (LOG_FORMAT=json): structured JSON for log aggregation tools.
"""
import logging
import sys
import time
from typing import Any, Callable

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure the root logger based on application settings.

    Call this once during application startup (inside the lifespan handler).
    Clears any existing handlers to prevent duplicate log lines during
    hot-reload in development.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if settings.LOG_FORMAT == "json":
        formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger instance.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Processing resume %s", resume_id)

    Args:
        name: Logger name — typically ``__name__`` of the calling module.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    return logging.getLogger(name)


class RequestLoggingMiddleware:
    """
    ASGI middleware that logs every HTTP request with timing information.

    Captures: HTTP method, path, response status code, and duration (ms).

    This is implemented as raw ASGI middleware rather than a Starlette
    ``BaseHTTPMiddleware`` to avoid the well-known issues with
    BaseHTTPMiddleware and streaming responses.
    """

    def __init__(self, app: Any) -> None:
        self.app = app
        self.logger = get_logger("api.request")

    async def __call__(
        self, scope: dict, receive: Callable, send: Callable
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        response_status: int = 500

        async def send_wrapper(message: dict) -> None:
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000, 2
            )
            method = scope.get("method", "UNKNOWN")
            path = scope.get("path", "/")
            self.logger.info(
                "%s %s -> %d (%.2fms)",
                method,
                path,
                response_status,
                duration_ms,
            )

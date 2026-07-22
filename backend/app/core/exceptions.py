"""
Centralized exception handling.

Defines a custom exception hierarchy for the application and registers
FastAPI exception handlers that return consistent, structured JSON responses.

Exception Hierarchy:
    AppException (base)
    ├── NotFoundError          — 404
    ├── FileValidationError    — 400
    ├── FileProcessingError    — 422
    ├── AIServiceError         — 503
    └── DatabaseError          — 500
"""
from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Custom Exception Hierarchy
# ---------------------------------------------------------------------------


class AppException(Exception):
    """
    Base exception for all application-level errors.

    Every custom exception inherits from this class so that a single
    FastAPI exception handler can catch all domain errors and format
    them into a consistent JSON response.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[Any] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: Any) -> None:
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class FileValidationError(AppException):
    """Raised when an uploaded file fails validation (type, size, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class FileProcessingError(AppException):
    """Raised when file parsing or text extraction fails."""

    def __init__(
        self, message: str, detail: Optional[Any] = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class AIServiceError(AppException):
    """Raised when an external AI service (Gemini) is unreachable or returns an error."""

    def __init__(
        self,
        message: str = "AI service is currently unavailable.",
        detail: Optional[Any] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )


class DatabaseError(AppException):
    """Raised when a database operation fails."""

    def __init__(
        self,
        message: str = "A database operation failed.",
        detail: Optional[Any] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


# ---------------------------------------------------------------------------
# JSON Error Response Builder
# ---------------------------------------------------------------------------


def _build_error_response(
    status_code: int,
    message: str,
    detail: Optional[Any] = None,
) -> JSONResponse:
    """
    Build a consistent JSON error response body.

    Every error returned by the API follows this shape:
    {
        "success": false,
        "error": {
            "message": "Human-readable error message",
            "status_code": 400,
            "detail": <optional extra info>
        }
    }
    """
    body: dict[str, Any] = {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
        },
    }
    if detail is not None:
        body["error"]["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


# ---------------------------------------------------------------------------
# FastAPI Exception Handlers
# ---------------------------------------------------------------------------


async def app_exception_handler(
    request: Request, exc: AppException
) -> JSONResponse:
    """Handle all custom AppException subclasses."""
    return _build_error_response(
        status_code=exc.status_code,
        message=exc.message,
        detail=exc.detail,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic / FastAPI request validation errors.
    Transforms the raw error list into a cleaner structure.
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )
    return _build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed.",
        detail=errors,
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Catch-all handler for any unhandled exception.
    Prevents raw stack traces from leaking to the client.
    """
    return _build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected internal error occurred.",
    )


# ---------------------------------------------------------------------------
# Registration Helper
# ---------------------------------------------------------------------------


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI application instance."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

"""Custom exception classes and global exception handlers.

Defines application-specific HTTP exceptions and registers handlers
that convert unhandled exceptions into consistent JSON responses
matching the APIResponse schema.
"""

import logging
import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception with HTTP status code."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=404, detail=detail)


class UnauthorizedException(AppException):
    """Raised when authentication is missing or invalid."""

    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(AppException):
    """Raised when the authenticated user lacks permission."""

    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(status_code=403, detail=detail)


class ConflictException(AppException):
    """Raised when the request conflicts with existing state."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(status_code=409, detail=detail)


class BadRequestException(AppException):
    """Raised when the request parameters are invalid."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=400, detail=detail)


# ===== Exception Handlers =====


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Convert AppException instances to a consistent JSON error response."""
    return _error_response(exc.status_code, exc.detail)


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Convert Starlette HTTPException to uniform APIResponse format.

    Handles 404 (Not Found), 405 (Method Not Allowed), and other
    framework-level HTTP errors.
    """
    return _error_response(exc.status_code, exc.detail)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic validation errors to a readable format.

    Extracts the first error message and returns 422.
    """
    messages: list[str] = []
    for error in exc.errors():
        loc = " -> ".join(str(part) for part in error["loc"])
        messages.append(f"{loc}: {error['msg']}")
    detail = "; ".join(messages) if messages else "Request validation failed"
    return _error_response(422, detail)


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler for unhandled exceptions.

    Logs the full traceback and returns a generic 500 error to the client.
    Does NOT leak internal error details in the response.
    """
    logger.error(
        "Unhandled exception on %s %s:\n%s",
        request.method,
        request.url.path,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
    return _error_response(500, "Internal server error")


def _error_response(status_code: int, detail: str) -> JSONResponse:
    """Build a uniform JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "message": detail,
            "data": None,
        },
    )

"""Custom exception classes and global exception handlers.

Defines application-specific HTTP exceptions and registers handlers
that convert unhandled exceptions into consistent JSON responses.
"""

from fastapi import Request
from fastapi.responses import JSONResponse


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


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Convert AppException instances to a consistent JSON error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )

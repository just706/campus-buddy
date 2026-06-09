"""Common Pydantic schemas shared across the API.

Defines the uniform API response wrapper and pagination model used by
all endpoints.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Uniform wrapper for all API responses."""

    code: int = Field(default=200, description="HTTP status code")
    message: str = Field(default="success", description="Human-readable message")
    data: T | None = Field(default=None, description="Response payload")


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedData(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T] = Field(default_factory=list)
    total: int = Field(default=0, description="Total item count")
    page: int = Field(default=1)
    page_size: int = Field(default=20)

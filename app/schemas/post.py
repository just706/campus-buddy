"""Post-related Pydantic schemas.

Request/response models for buddy-finding post operations.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    """Payload for creating a new buddy post."""

    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    description: str = Field(default="", max_length=5000, description="Post body")
    category: str = Field(
        ..., min_length=1, max_length=20, description="study | sports | dining | travel | other"
    )
    tags: list[str] | None = Field(default=None, description="Custom tag list")
    target_count: int = Field(default=1, ge=1, le=100, description="How many buddies needed")
    location: str | None = Field(default=None, max_length=200, description="Meeting place")
    time_range: str | None = Field(default=None, max_length=200, description="e.g. '每周三下午'")
    expires_at: datetime | None = Field(default=None, description="Auto-close after this time")


class PostUpdate(BaseModel):
    """Payload for updating an existing post (partial update)."""

    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    category: str | None = Field(default=None, max_length=20)
    tags: list[str] | None = Field(default=None)
    target_count: int | None = Field(default=None, ge=1, le=100)
    location: str | None = Field(default=None, max_length=200)
    time_range: str | None = Field(default=None, max_length=200)
    expires_at: datetime | None = Field(default=None)


class PostFilter(BaseModel):
    """Query parameters for listing/filtering posts."""

    category: str | None = Field(default=None, description="Filter by category")
    tag: str | None = Field(default=None, description="Filter by a single tag")
    status: str | None = Field(default=None, description="active | closed | cancelled")
    keyword: str | None = Field(default=None, description="Search in title and description")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PostUserBrief(BaseModel):
    """Minimal author info embedded in post responses."""

    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    university: str
    college: str | None = None
    major: str | None = None
    grade: str | None = None

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    """Post data returned by the API."""

    id: int
    user_id: int
    title: str
    description: str
    category: str
    tags: list | None = None
    target_count: int
    current_count: int
    location: str | None = None
    time_range: str | None = None
    status: str
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    user: PostUserBrief | None = None

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    """Paginated post list."""

    items: list[PostResponse]
    total: int
    page: int
    page_size: int

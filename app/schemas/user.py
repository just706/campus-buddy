"""User-related Pydantic schemas.

Request/response models for user profile operations.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Public user profile returned by the API."""

    id: int
    username: str
    email: str
    phone: str | None = None
    university: str
    college: str | None = None
    major: str | None = None
    grade: str | None = None
    nickname: str | None = None
    avatar: str | None = None
    gender: str | None = None
    bio: str | None = None
    tags: list | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Fields the user can update on their own profile."""

    nickname: str | None = Field(default=None, max_length=50, description="Display name")
    avatar: str | None = Field(default=None, max_length=500, description="Avatar URL")
    gender: str | None = Field(default=None, max_length=10, description="Gender")
    bio: str | None = Field(default=None, max_length=500, description="Short bio")
    tags: list[str] | None = Field(default=None, description="Interest tags")
    phone: str | None = Field(default=None, max_length=20, description="Phone number")
    university: str | None = Field(default=None, max_length=100, description="University")
    college: str | None = Field(default=None, max_length=100)
    major: str | None = Field(default=None, max_length=100)
    grade: str | None = Field(default=None, max_length=20)

"""Auth-related Pydantic schemas.

Request/response models for registration, login, and token refresh.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Registration payload."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    email: EmailStr = Field(..., description="Email address, used for verification")
    password: str = Field(
        ..., min_length=6, max_length=128, description="Password (6-128 chars)"
    )
    phone: str | None = Field(default=None, max_length=20, description="Phone number")
    university: str = Field(
        ..., min_length=1, max_length=100, description="University name"
    )
    college: str | None = Field(default=None, max_length=100, description="College")
    major: str | None = Field(default=None, max_length=100, description="Major")
    grade: str | None = Field(default=None, max_length=20, description="Grade")
    nickname: str | None = Field(default=None, max_length=50, description="Display name")
    gender: str | None = Field(default=None, max_length=10, description="Gender")


class LoginRequest(BaseModel):
    """Login payload — supports email or username."""

    login: str = Field(..., min_length=1, max_length=100, description="Email or username")
    password: str = Field(..., min_length=1, max_length=128, description="Password")


class TokenResponse(BaseModel):
    """JWT token pair returned on login or refresh."""

    access_token: str = Field(..., description="Short-lived access token (15 min)")
    refresh_token: str = Field(..., description="Long-lived refresh token (7 days)")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshRequest(BaseModel):
    """Refresh token payload."""

    refresh_token: str = Field(..., description="The refresh token from login")

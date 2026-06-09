"""Authentication API endpoints.

Handles user registration, login, and token refresh.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import APIResponse
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=APIResponse[UserResponse], status_code=201)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[UserResponse]:
    """Register a new campus buddy account.

    Requires a unique username and email. Password must be 6-128 characters.
    School information (university) is required for AI matching.
    """
    user = await auth_service.register(db, data)
    return APIResponse(
        code=201,
        message="Registration successful",
        data=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TokenResponse]:
    """Login with email or username and password.

    Returns an access token (15 min) and refresh token (7 days).
    Use the access token in the Authorization header for authenticated requests.
    """
    tokens = await auth_service.login(db, data.login, data.password)
    return APIResponse(data=tokens)


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh(
    data: RefreshRequest,
) -> APIResponse[TokenResponse]:
    """Refresh an expired access token using a valid refresh token.

    Returns a new access token and refresh token pair.
    """
    tokens = await auth_service.refresh_token(data.refresh_token)
    return APIResponse(data=tokens)

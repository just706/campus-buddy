"""FastAPI dependencies for authentication and database access.

Provides reusable dependency functions injected into route handlers.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends, Header
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


async def get_current_user(
    authorization: str = Header(..., description="Bearer <JWT token>"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from the Authorization header.

    Usage:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            ...

    Args:
        authorization: The Authorization header value (e.g. "Bearer xxx").
        db: Injected async database session.

    Returns:
        The authenticated User ORM object.

    Raises:
        UnauthorizedException: If the token is missing, expired, or invalid,
                               or if the user no longer exists.
    """
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing or malformed Authorization header")

    token = authorization.removeprefix("Bearer ")

    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Token is not an access token")

    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise UnauthorizedException("Token payload missing user_id")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is disabled")

    return user

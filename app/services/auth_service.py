"""Authentication business logic.

Handles user registration, login, and token refresh. Orchestrates
between the database layer and the security module.
"""

from jose import JWTError
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse


async def register(db: AsyncSession, data: RegisterRequest) -> User:
    """Create a new user account.

    Args:
        db: Async database session.
        data: Validated registration payload.

    Returns:
        The newly created User object.

    Raises:
        ConflictException: If the username or email is already taken.
    """
    # Check for duplicate username or email
    existing = await db.execute(
        select(User).where(
            or_(User.username == data.username, User.email == data.email)
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("Username or email already registered")

    user = User(
        username=data.username,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        university=data.university,
        college=data.college,
        major=data.major,
        grade=data.grade,
        nickname=data.nickname,
        gender=data.gender,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login(db: AsyncSession, login_id: str, password: str) -> TokenResponse:
    """Authenticate a user and return JWT tokens.

    Accepts either email or username as the login identifier.

    Args:
        db: Async database session.
        login_id: Email or username.
        password: Plain-text password.

    Returns:
        A TokenResponse with access and refresh tokens.

    Raises:
        UnauthorizedException: If credentials are invalid or user is disabled.
    """
    result = await db.execute(
        select(User).where(
            or_(User.email == login_id, User.username == login_id)
        )
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Invalid credentials")

    if not user.is_active:
        raise UnauthorizedException("Account is disabled")

    return TokenResponse(
        access_token=create_access_token(user.id, user.username),
        refresh_token=create_refresh_token(user.id, user.username),
    )


async def refresh_token(refresh_token_str: str) -> TokenResponse:
    """Issue a new access token from a valid refresh token.

    Args:
        refresh_token_str: The refresh token obtained at login.

    Returns:
        A new TokenResponse with fresh access and refresh tokens.

    Raises:
        UnauthorizedException: If the refresh token is invalid, expired,
                               or not a refresh-type token.
    """
    try:
        payload = decode_token(refresh_token_str)
    except JWTError:
        raise UnauthorizedException("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Token is not a refresh token")

    user_id = payload.get("user_id")
    username = payload.get("sub")

    if user_id is None or username is None:
        raise UnauthorizedException("Invalid refresh token payload")

    return TokenResponse(
        access_token=create_access_token(user_id, username),
        refresh_token=create_refresh_token(user_id, username),
    )

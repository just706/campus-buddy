"""Security utilities — JWT token creation/verification and password hashing."""

from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ===== Password Hashing =====


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    The password is truncated to 72 bytes (bcrypt's max) before hashing.
    Returns the hash as a UTF-8 string for storage.
    """
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ===== JWT =====
def create_access_token(user_id: int, username: str) -> str:
    """Create a short-lived JWT access token.

    Args:
        user_id: The user's database ID.
        username: The user's username (embedded as the JWT subject).

    Returns:
        An encoded JWT string valid for ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "user_id": user_id,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int, username: str) -> str:
    """Create a long-lived JWT refresh token.

    Args:
        user_id: The user's database ID.
        username: The user's username.

    Returns:
        An encoded JWT string valid for REFRESH_TOKEN_EXPIRE_DAYS.
    """
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": username,
        "user_id": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token.

    Args:
        token: The encoded JWT string.

    Returns:
        The decoded payload dict.

    Raises:
        JWTError: If the token is expired, invalid, or malformed.
    """
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

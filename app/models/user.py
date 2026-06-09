"""User ORM model.

Represents a registered user with account credentials, school profile,
and interest tags used for AI-powered matching.
"""

from sqlalchemy import Boolean, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    """Campus buddy user account.

    Stores authentication data, school information, and personal profile.
    The tags column uses JSON to store a flexible list of interest labels
    (e.g. ["Python", "羽毛球", "期末复习"]) for AI matching.
    """

    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # ===== School Info =====
    university: Mapped[str] = mapped_column(String(100), nullable=False)
    college: Mapped[str | None] = mapped_column(String(100), nullable=True)
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ===== Profile =====
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ===== Interests (JSON: list of tag strings) =====
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ===== Status =====
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

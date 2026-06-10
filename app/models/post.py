"""Post ORM model.

Represents a campus buddy-finding post created by a user.
Supports categories, flexible JSON tags, participant counting,
and automatic expiry.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Post(Base):
    """A campus buddy-finding post.

    Each post belongs to one user and describes what kind of buddy
    they are looking for. The tags column stores a flexible JSON list
    (e.g. ["期末复习", "图书馆"]) for AI matching and filtering.
    """

    __tablename__ = "post"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # study | sports | dining | travel | other
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    target_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    time_range: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="active", index=True, nullable=False
    )  # active | closed | cancelled
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship: eagerly load author info for post display
    user: Mapped["User"] = relationship("User")

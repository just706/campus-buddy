"""Notification ORM model.

Stores system notifications sent to users for match results,
new messages, and system announcements.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Notification(Base):
    """User notification.

    Created automatically by services when a match succeeds, a message
    arrives, or a system event occurs.
    """

    __tablename__ = "notification"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), index=True, nullable=False
    )
    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "match" | "message" | "system"
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

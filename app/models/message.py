"""Message ORM model.

Stores individual messages within a chat session, supporting both text
and image content types.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Message(Base):
    """A single message in a chat conversation.

    Supports text and image content types. Tracks read status for
    notification badges.
    """

    __tablename__ = "message"

    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chat.id"), index=True, nullable=False
    )
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), index=True, nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_type: Mapped[str] = mapped_column(
        String(20), default="text", nullable=False
    )  # text | image
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

"""Match ORM model.

Represents a buddy match between two users — one who initiates the request
and a target user who accepts or rejects it. On acceptance, a chat session
is created atomically.
"""

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Match(Base):
    """A matching record between two users.

    Created when one user requests to match with another (possibly via
    a specific post). On acceptance, status moves from 'pending' to
    'accepted' and a Chat is created in the same transaction.
    """

    __tablename__ = "match"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), index=True, nullable=False
    )
    target_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), index=True, nullable=False
    )
    post_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("post.id"), nullable=True
    )
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True, nullable=False
    )  # pending | accepted | rejected

"""Chat ORM model.

Represents a one-to-one chat session between two matched users.
Created atomically when a match is accepted.
"""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Chat(Base):
    """A one-to-one chat session tied to an accepted match.

    Each match can have at most one chat (enforced by UNIQUE on match_id).
    """

    __tablename__ = "chat"

    match_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("match.id"), unique=True, index=True, nullable=False
    )
    user1_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )
    user2_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )

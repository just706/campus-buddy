"""Base ORM model with shared columns and utilities.

All database models inherit from Base to get id, created_at, and
updated_at columns automatically.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Abstract base class for all ORM models.

    Provides:
    - id: Integer primary key
    - created_at: UTC timestamp set on insert
    - updated_at: UTC timestamp updated on every change
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

"""User profile business logic.

Handles profile retrieval, update, and related operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdateRequest


async def update_profile(db: AsyncSession, user: User, data: UserUpdateRequest) -> User:
    """Update fields on the authenticated user's profile.

    Only non-None fields in the request are applied (partial update).

    Args:
        db: Async database session.
        user: The authenticated User ORM object.
        data: The fields to update (partial).

    Returns:
        The updated User object.
    """
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

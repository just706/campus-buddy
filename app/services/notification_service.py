"""Notification business logic.

Handles notification listing, single/batch read marking, and unread count.
Notifications are created automatically by other services (match, chat).
"""

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.notification import Notification
from app.models.user import User


async def get_notifications(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
) -> tuple[list[Notification], int, int]:
    """List notifications for the current user, newest first.

    Args:
        db: Async database session.
        current_user: The authenticated user.
        page: Page number.
        page_size: Items per page.
        unread_only: If True, only return unread notifications.

    Returns:
        A tuple of (notifications_list, total_count, unread_count).
    """
    conditions = [Notification.user_id == current_user.id]
    if unread_only:
        conditions.append(Notification.is_read == False)  # noqa: E712

    base = select(Notification).where(*conditions)

    # Total count
    count_query = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Unread count (always across all notifications)
    unread_result = await db.execute(
        select(func.count()).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    unread_count = unread_result.scalar_one()

    # Pagination
    offset = (page - 1) * page_size
    query = (
        base.order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    notifications = list(result.scalars().all())

    return notifications, total, unread_count


async def mark_read(
    db: AsyncSession,
    notification_id: int,
    current_user: User,
) -> Notification:
    """Mark a single notification as read.

    Args:
        db: Async database session.
        notification_id: The notification to mark.
        current_user: The authenticated user (must be the owner).

    Returns:
        The updated Notification.

    Raises:
        NotFoundException: If the notification doesn't exist.
        ForbiddenException: If it belongs to another user.
    """
    notification = await db.get(Notification, notification_id)
    if notification is None:
        raise NotFoundException("Notification not found")

    if notification.user_id != current_user.id:
        raise ForbiddenException("Not your notification")

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_read(
    db: AsyncSession,
    current_user: User,
) -> int:
    """Mark all of the current user's notifications as read.

    Args:
        db: Async database session.
        current_user: The authenticated user.

    Returns:
        The number of notifications marked as read.
    """
    stmt = (
        update(Notification)
        .where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def mark_batch_read(
    db: AsyncSession,
    ids: list[int],
    current_user: User,
) -> int:
    """Mark a batch of notifications as read.

    Silently skips notifications that don't belong to the current user
    or are already read.

    Args:
        db: Async database session.
        ids: List of notification IDs to mark read.
        current_user: The authenticated user.

    Returns:
        The number of notifications actually marked as read.
    """
    stmt = (
        update(Notification)
        .where(
            Notification.id.in_(ids),
            Notification.user_id == current_user.id,
            Notification.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount

"""Notification API endpoints.

REST endpoints for listing notifications and marking them as read.
Notifications themselves are created automatically by other services
(match_service, chat_service) and have no create endpoint here.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.notification import (
    BatchReadRequest,
    NotificationListResponse,
    NotificationResponse,
)
from app.services import notification_service

router = APIRouter(prefix="/notifications")


@router.get("", response_model=APIResponse[NotificationListResponse])
async def list_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    unread_only: bool = Query(default=False, description="Only show unread notifications"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[NotificationListResponse]:
    """List my notifications, newest first.

    Optionally filter to unread-only. The response includes total unread
    count for badge display.
    """
    items, total, unread_count = await notification_service.get_notifications(
        db, current_user, page=page, page_size=page_size, unread_only=unread_only
    )
    return APIResponse(
        data=NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            page=page,
            page_size=page_size,
            unread_count=unread_count,
        )
    )


@router.put(
    "/{notification_id}/read",
    response_model=APIResponse[NotificationResponse],
)
async def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[NotificationResponse]:
    """Mark a single notification as read.

    Only the notification owner can mark it as read.
    """
    notification = await notification_service.mark_read(
        db, notification_id, current_user
    )
    return APIResponse(
        message="Notification marked as read",
        data=NotificationResponse.model_validate(notification),
    )


@router.put(
    "/read-all",
    response_model=APIResponse[int],
)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[int]:
    """Mark all my notifications as read."""
    count = await notification_service.mark_all_read(db, current_user)
    return APIResponse(
        message=f"{count} notification(s) marked as read",
        data=count,
    )


@router.put(
    "/batch-read",
    response_model=APIResponse[int],
)
async def batch_read(
    body: BatchReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[int]:
    """Mark a batch of notifications as read by ID."""
    count = await notification_service.mark_batch_read(
        db, body.ids, current_user
    )
    return APIResponse(
        message=f"{count} notification(s) marked as read",
        data=count,
    )

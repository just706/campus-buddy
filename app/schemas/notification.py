"""Notification Pydantic schemas.

Request/response models for system, match, and message notifications.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """A single notification returned by the API."""

    id: int
    user_id: int
    type: str  # match | message | system
    title: str
    content: str
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Paginated notification list."""

    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int = 0


class BatchReadRequest(BaseModel):
    """Payload for marking multiple notifications as read."""

    ids: list[int] = Field(..., min_length=1, max_length=100, description="Notification IDs to mark read")

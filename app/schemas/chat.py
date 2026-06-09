"""Chat and Message Pydantic schemas.

Request/response models for chat sessions and message operations.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# ===== Message Schemas =====


class MessageResponse(BaseModel):
    """A single message as returned by the API."""

    id: int
    chat_id: int
    sender_id: int
    content: str
    content_type: str = "text"  # text | image
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    """Paginated message history."""

    items: list[MessageResponse]
    total: int
    page: int
    page_size: int


class SendMessageRequest(BaseModel):
    """Payload for sending a message (HTTP fallback)."""

    content: str = Field(..., min_length=1, max_length=5000, description="Message body")
    content_type: str = Field(default="text", pattern=r"^(text|image)$")


# ===== WebSocket Message Protocol =====


class WsClientMessage(BaseModel):
    """Message sent from client to server via WebSocket."""

    type: str = Field(default="message", pattern=r"^(message|ping)$")
    content: str = Field(default="", max_length=5000)
    content_type: str = Field(default="text", pattern=r"^(text|image)$")


class WsServerMessage(BaseModel):
    """Message sent from server to client via WebSocket."""

    type: str  # message | system | pong | error
    message_id: int | None = None
    chat_id: int | None = None
    sender_id: int | None = None
    sender_nickname: str | None = None
    sender_avatar: str | None = None
    content: str | None = None
    content_type: str | None = None
    created_at: str | None = None  # ISO 8601
    # For system messages
    action: str | None = None
    user_id: int | None = None
    # For errors
    reason: str | None = None
    detail: str | None = None


# ===== Chat Session Schemas =====


class ChatBriefResponse(BaseModel):
    """Brief chat session info for the chat list."""

    id: int
    match_id: int
    user1_id: int
    user2_id: int
    other_user_nickname: str | None = None
    other_user_avatar: str | None = None
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatListResponse(BaseModel):
    """Paginated chat session list."""

    items: list[ChatBriefResponse]
    total: int
    page: int
    page_size: int

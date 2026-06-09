"""Chat business logic.

Handles chat session management, message sending (with AI moderation),
message history retrieval, and read-status tracking.
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.chat import Chat
from app.models.message import Message
from app.models.notification import Notification
from app.models.user import User
from app.services.moderation_service import moderate_content

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(UTC)


async def get_my_chats(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """List chat sessions for the current user.

    Includes the other user's nickname/avatar, the last message preview,
    and unread message count.

    Args:
        db: Async database session.
        current_user: The authenticated user.
        page: Page number (1-indexed).
        page_size: Items per page.

    Returns:
        A tuple of (chat_dicts_list, total_count).
    """
    # Only chats where the user is a participant
    conditions = [
        or_(
            Chat.user1_id == current_user.id,
            Chat.user2_id == current_user.id,
        )
    ]
    base = select(Chat).where(*conditions)

    # Count total
    count_query = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Paginate
    offset = (page - 1) * page_size
    query = (
        base.order_by(Chat.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    chats = list(result.scalars().all())

    # Enrich each chat with contextual data
    enriched: list[dict] = []
    for chat in chats:
        # Determine the other user
        other_id = (
            chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
        )
        other_user = await db.get(User, other_id)

        # Last message preview
        last_msg_result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = last_msg_result.scalar_one_or_none()

        # Unread count (messages not sent by current_user and not read)
        unread_result = await db.execute(
            select(func.count())
            .select_from(Message)
            .where(
                Message.chat_id == chat.id,
                Message.sender_id != current_user.id,
                Message.is_read == False,  # noqa: E712
            )
        )
        unread_count = unread_result.scalar_one()

        enriched.append({
            "id": chat.id,
            "match_id": chat.match_id,
            "user1_id": chat.user1_id,
            "user2_id": chat.user2_id,
            "other_user_nickname": (
                other_user.nickname or other_user.username if other_user else None
            ),
            "other_user_avatar": other_user.avatar if other_user else None,
            "last_message": last_msg.content[:100] if last_msg else None,
            "last_message_at": last_msg.created_at if last_msg else None,
            "unread_count": unread_count,
            "created_at": chat.created_at,
        })

    return enriched, total


async def get_messages(
    db: AsyncSession,
    chat_id: int,
    current_user: User,
    page: int = 1,
    page_size: int = 50,
    since_id: int | None = None,
) -> tuple[list[Message], int]:
    """Retrieve message history for a chat.

    Args:
        db: Async database session.
        chat_id: The chat session ID.
        current_user: The authenticated user (must be a participant).
        page: Page number.
        page_size: Messages per page.
        since_id: If set, only return messages with id > since_id (incremental pull).

    Returns:
        A tuple of (messages_list, total_count).

    Raises:
        NotFoundException: If the chat doesn't exist.
        ForbiddenException: If the user is not a participant.
    """
    chat = await db.get(Chat, chat_id)
    if chat is None:
        raise NotFoundException("Chat not found")

    if current_user.id not in (chat.user1_id, chat.user2_id):
        raise ForbiddenException("Not a participant of this chat")

    conditions = [Message.chat_id == chat_id]
    if since_id is not None:
        conditions.append(Message.id > since_id)

    base = select(Message).where(*conditions)

    count_query = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    query = (
        base.order_by(Message.created_at.asc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    messages = list(result.scalars().all())

    return messages, total


async def send_message(
    db: AsyncSession,
    chat_id: int,
    sender: User,
    content: str,
    content_type: str = "text",
) -> Message:
    """Send a message in a chat. Runs AI moderation before persisting.

    If moderation blocks the content, the message is rejected.
    Also creates a notification for the other participant.

    Args:
        db: Async database session.
        chat_id: The target chat session.
        sender: The authenticated user sending the message.
        content: Message body.
        content_type: 'text' or 'image'.

    Returns:
        The newly created Message.

    Raises:
        NotFoundException: If the chat doesn't exist.
        ForbiddenException: If sender is not a participant.
        BadRequestException: If AI moderation blocks the content.
    """
    chat = await db.get(Chat, chat_id)
    if chat is None:
        raise NotFoundException("Chat not found")

    if sender.id not in (chat.user1_id, chat.user2_id):
        raise ForbiddenException("Not a participant of this chat")

    # AI moderation
    if content.strip() and content_type == "text":
        decision = await moderate_content(content, context="chat message")
        logger.info(
            "Chat moderation: action=%s confidence=%.2f reason=%s",
            decision.action,
            decision.result.confidence,
            decision.result.reason,
        )
        if decision.action == "block":
            raise BadRequestException(
                f"Message violates community guidelines: {decision.result.reason}"
            )

    # Persist message
    message = Message(
        chat_id=chat_id,
        sender_id=sender.id,
        content=content,
        content_type=content_type,
    )
    db.add(message)
    await db.flush()

    # Notify the other participant
    other_id = chat.user2_id if chat.user1_id == sender.id else chat.user1_id
    sender_name = sender.nickname or sender.username
    preview = content[:50] + ("..." if len(content) > 50 else "")
    notification = Notification(
        user_id=other_id,
        type="message",
        title="新消息",
        content=f"{sender_name}: {preview}",
    )
    db.add(notification)

    await db.commit()
    await db.refresh(message)
    return message


async def mark_messages_read(
    db: AsyncSession,
    chat_id: int,
    current_user: User,
    up_to_id: int | None = None,
) -> int:
    """Mark messages as read for the current user in a chat.

    Only marks messages NOT sent by the current user that are still unread.

    Args:
        db: Async database session.
        chat_id: The chat session.
        current_user: The authenticated user.
        up_to_id: If set, only mark messages with id <= up_to_id.

    Returns:
        The number of messages marked as read.
    """
    chat = await db.get(Chat, chat_id)
    if chat is None:
        raise NotFoundException("Chat not found")

    if current_user.id not in (chat.user1_id, chat.user2_id):
        raise ForbiddenException("Not a participant of this chat")

    conditions = [
        Message.chat_id == chat_id,
        Message.sender_id != current_user.id,
        Message.is_read == False,  # noqa: E712
    ]
    if up_to_id is not None:
        conditions.append(Message.id <= up_to_id)

    stmt = (
        update(Message)
        .where(*conditions)
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    await db.commit()

    count = result.rowcount
    return count


async def get_chat_participant_ids(
    db: AsyncSession, chat_id: int
) -> tuple[int, int] | None:
    """Get the two user IDs for a chat session.

    Args:
        db: Async database session.
        chat_id: The chat session ID.

    Returns:
        A tuple of (user1_id, user2_id) or None if the chat doesn't exist.
    """
    chat = await db.get(Chat, chat_id)
    if chat is None:
        return None
    return (chat.user1_id, chat.user2_id)

"""Chat API endpoints — HTTP chat/message operations and WebSocket.

Provides REST endpoints for listing chats and message history,
plus a WebSocket endpoint for real-time bidirectional messaging.
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.core.ws_manager import ws_manager
from app.models.user import User
from app.schemas.chat import (
    ChatBriefResponse,
    ChatListResponse,
    MessageListResponse,
    MessageResponse,
    SendMessageRequest,
    WsClientMessage,
    WsServerMessage,
)
from app.schemas.common import APIResponse
from app.services import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chats")
ws_router = APIRouter(prefix="/ws")


# ================================================================
# HTTP Endpoints
# ================================================================


@router.get("", response_model=APIResponse[ChatListResponse])
async def list_my_chats(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ChatListResponse]:
    """List my chat sessions.

    Each chat includes the other user's info, last message preview,
    and unread message count. Sorted by newest first.
    """
    enriched, total = await chat_service.get_my_chats(
        db, current_user, page=page, page_size=page_size
    )

    items = [ChatBriefResponse(**c) for c in enriched]
    return APIResponse(
        data=ChatListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get(
    "/{chat_id}/messages",
    response_model=APIResponse[MessageListResponse],
)
async def get_messages(
    chat_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    since_id: int | None = Query(default=None, description="Incremental pull: get messages after this ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MessageListResponse]:
    """Get message history for a chat session.

    Messages are ordered oldest-first. Use `since_id` for incremental
    polling after a WebSocket disconnect (get only new messages).
    """
    messages, total = await chat_service.get_messages(
        db, chat_id, current_user, page=page, page_size=page_size, since_id=since_id
    )
    return APIResponse(
        data=MessageListResponse(
            items=[MessageResponse.model_validate(m) for m in messages],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post(
    "/{chat_id}/messages",
    response_model=APIResponse[MessageResponse],
    status_code=201,
)
async def send_message_http(
    chat_id: int,
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MessageResponse]:
    """Send a message via HTTP (fallback for when WebSocket is unavailable).

    Prefer WebSocket for real-time chat. This endpoint is useful when the
    client can't maintain a persistent connection.
    """
    message = await chat_service.send_message(
        db, chat_id, current_user, body.content, body.content_type
    )

    # Try to push via WebSocket if the other user is online
    participants = await chat_service.get_chat_participant_ids(db, chat_id)
    if participants:
        other_id = participants[1] if participants[0] == current_user.id else participants[0]
        sender_nickname = current_user.nickname or current_user.username
        ws_payload = {
            "type": "message",
            "message_id": message.id,
            "chat_id": chat_id,
            "sender_id": current_user.id,
            "sender_nickname": sender_nickname,
            "sender_avatar": current_user.avatar,
            "content": message.content,
            "content_type": message.content_type,
            "created_at": message.created_at.isoformat() if message.created_at else None,
        }
        await ws_manager.send_to_chat(chat_id, current_user.id, other_id, ws_payload)

    return APIResponse(
        code=201,
        message="Message sent",
        data=MessageResponse.model_validate(message),
    )


@router.post(
    "/{chat_id}/messages/read",
    response_model=APIResponse[int],
)
async def mark_read(
    chat_id: int,
    up_to_id: int | None = Query(default=None, description="Mark messages up to this ID as read"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[int]:
    """Mark unread messages in a chat as read.

    Only marks messages NOT sent by the current user.
    Optionally specify up_to_id to only mark messages up to a certain point.
    """
    count = await chat_service.mark_messages_read(
        db, chat_id, current_user, up_to_id=up_to_id
    )
    return APIResponse(
        message=f"{count} message(s) marked as read",
        data=count,
    )


# ================================================================
# WebSocket Endpoint
# ================================================================


async def _authenticate_ws(websocket: WebSocket, db: AsyncSession) -> User:
    """Authenticate a WebSocket connection from the query token.

    Args:
        websocket: The WebSocket connection (pre-accept).
        db: Async database session for user lookup.

    Returns:
        The authenticated User.

    Raises:
        UnauthorizedException: If authentication fails — caller should
            close the WebSocket with an appropriate error code.
    """
    token = websocket.query_params.get("token")
    if not token:
        raise UnauthorizedException("Missing token in query parameter")

    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Token is not an access token")

    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise UnauthorizedException("Token payload missing user_id")

    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise UnauthorizedException("User not found")

    return user


@ws_router.websocket("/chat/{chat_id}")
async def websocket_chat(
    websocket: WebSocket,
    chat_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """WebSocket endpoint for real-time chat.

    Connect to: `ws://host/api/v1/ws/chat/{chat_id}?token={jwt_access_token}`

    ## Message Protocol

    ### Client → Server:
    ```json
    {"type": "message", "content": "Hello!", "content_type": "text"}
    {"type": "ping"}
    ```

    ### Server → Client:
    ```json
    {"type": "message", "message_id": 1, "chat_id": 1, "sender_id": 2,
     "sender_nickname": "小明", "content": "Hello!", "content_type": "text",
     "created_at": "..."}
    {"type": "system", "action": "user_online", "user_id": 2}
    {"type": "pong"}
    {"type": "error", "reason": "...", "detail": "..."}
    ```

    ## Heartbeat
    Client should send `{"type":"ping"}` every 30 seconds. The server
    replies with `{"type":"pong"}`. No response within 60s → connection
    may be considered dead.
    """
    # Authenticate
    try:
        user = await _authenticate_ws(websocket, db)
    except UnauthorizedException as exc:
        await websocket.close(code=4001, reason=exc.detail)
        return

    # Validate chat participation
    participants = await chat_service.get_chat_participant_ids(db, chat_id)
    if participants is None:
        await websocket.close(code=4004, reason="Chat not found")
        return
    if user.id not in participants:
        await websocket.close(code=4003, reason="Not a participant of this chat")
        return

    other_user_id = participants[1] if participants[0] == user.id else participants[0]

    # Accept and register
    await ws_manager.connect(user.id, websocket)
    logger.info("WS chat: user=%d chat=%d", user.id, chat_id)

    # Notify the other user that this user is online
    await ws_manager.broadcast_system(other_user_id, "user_online", chat_id)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "reason": "invalid_json",
                    "detail": "Could not parse message as JSON",
                }, ensure_ascii=False))
                continue

            msg_type = data.get("type")

            # Heartbeat
            if msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            # Chat message
            if msg_type == "message":
                content = data.get("content", "")
                content_type = data.get("content_type", "text")

                if not content.strip():
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "reason": "empty_content",
                        "detail": "Message content cannot be empty",
                    }, ensure_ascii=False))
                    continue

                try:
                    message = await chat_service.send_message(
                        db, chat_id, user, content, content_type
                    )
                except Exception as exc:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "reason": "send_failed",
                        "detail": str(exc),
                    }, ensure_ascii=False))
                    continue

                sender_name = user.nickname or user.username
                ws_payload = {
                    "type": "message",
                    "message_id": message.id,
                    "chat_id": chat_id,
                    "sender_id": user.id,
                    "sender_nickname": sender_name,
                    "sender_avatar": user.avatar,
                    "content": message.content,
                    "content_type": message.content_type,
                    "created_at": message.created_at.isoformat() if message.created_at else None,
                }

                # Push to the other user if online
                await ws_manager.send_to_chat(
                    chat_id, user.id, other_user_id, ws_payload
                )

                continue

            # Unknown message type
            await websocket.send_text(json.dumps({
                "type": "error",
                "reason": "unknown_type",
                "detail": f"Unknown message type: {msg_type}",
            }, ensure_ascii=False))

    except WebSocketDisconnect:
        logger.info("WS disconnect: user=%d chat=%d", user.id, chat_id)
    except Exception:
        logger.exception("WS error: user=%d chat=%d", user.id, chat_id)
    finally:
        ws_manager.disconnect(user.id, websocket)
        await ws_manager.broadcast_system(other_user_id, "user_offline", chat_id)

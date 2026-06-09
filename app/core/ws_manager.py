"""WebSocket connection manager.

Manages active WebSocket connections for real-time chat messaging.
Supports multi-device connections per user, heartbeat keep-alive,
and targeted message delivery.
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time chat.

    Each user can have multiple connections (phone + desktop, etc.).
    Messages targeted at a user are broadcast to all their active connections.

    Usage:
        manager = ConnectionManager()

        # In WebSocket endpoint:
        await manager.connect(user_id, websocket)
        try:
            while True:
                data = await websocket.receive_text()
                ...
        finally:
            manager.disconnect(user_id, websocket)
    """

    def __init__(self) -> None:
        # {user_id: [WebSocket, WebSocket, ...]}
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection and register it.

        Args:
            user_id: The authenticated user's ID.
            websocket: The accepted WebSocket connection.
        """
        await websocket.accept()
        self._connections.setdefault(user_id, []).append(websocket)
        logger.info("WebSocket connected: user_id=%d (total=%d)", user_id, len(self._connections))

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.

        Args:
            user_id: The user whose connection is closing.
            websocket: The WebSocket to remove.
        """
        conns = self._connections.get(user_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self._connections.pop(user_id, None)
        logger.info("WebSocket disconnected: user_id=%d (remaining=%d)", user_id, len(conns))

    def is_online(self, user_id: int) -> bool:
        """Check if a user has any active WebSocket connections.

        Args:
            user_id: The user to check.

        Returns:
            True if the user has at least one active connection.
        """
        return user_id in self._connections and len(self._connections[user_id]) > 0

    def get_online_count(self) -> int:
        """Return the number of users with active connections."""
        return len(self._connections)

    async def send_to_user(self, user_id: int, message: dict[str, Any]) -> None:
        """Send a JSON message to all active connections of a user.

        Args:
            user_id: The target user.
            message: A JSON-serializable dict to send.
        """
        conns = self._connections.get(user_id, [])
        if not conns:
            return

        payload = json.dumps(message, ensure_ascii=False)
        dead: list[WebSocket] = []

        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
                logger.warning("Failed to send to user_id=%d, marking dead", user_id)

        # Clean up dead connections
        for ws in dead:
            self.disconnect(user_id, ws)

    async def send_to_chat(
        self,
        chat_id: int,
        sender_id: int,
        target_user_id: int,
        message: dict[str, Any],
    ) -> None:
        """Send a message to the other participant in a chat.

        Args:
            chat_id: The chat session ID.
            sender_id: The user who sent the message (not targeted).
            target_user_id: The user to deliver the message to.
            message: The message payload to send.
        """
        message["chat_id"] = chat_id
        message["sender_id"] = sender_id
        await self.send_to_user(target_user_id, message)

    async def broadcast_system(
        self, user_id: int, action: str, chat_id: int | None = None
    ) -> None:
        """Send a system event (e.g. user online/offline) to a user.

        Args:
            user_id: The target user.
            action: System action identifier.
            chat_id: Optional chat context.
        """
        msg: dict[str, Any] = {"type": "system", "action": action}
        if chat_id is not None:
            msg["chat_id"] = chat_id
        await self.send_to_user(user_id, msg)


# Global singleton
ws_manager = ConnectionManager()

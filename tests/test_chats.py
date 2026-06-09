"""Tests for the Chat module — session listing, message sending, history."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.ai.moderation import ModerationResult
from app.services.moderation_service import ModerationDecision


# ===== Helpers =====


async def _register_and_login(client: AsyncClient, username: str, email: str) -> str:
    """Register a user and return an access token."""
    await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": "test123456",
        "university": "测试大学",
        "nickname": username,
    })
    resp = await client.post("/api/v1/auth/login", json={
        "login": username,
        "password": "test123456",
    })
    return resp.json()["data"]["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _get_my_id(client: AsyncClient, token: str) -> int:
    """Get the current user's ID."""
    resp = await client.get("/api/v1/users/me", headers=_auth_header(token))
    return resp.json()["data"]["id"]


async def _create_accepted_match(
    client: AsyncClient, token_a: str, token_b: str
) -> tuple[int, int]:
    """Create user A, user B, let A request match with B, and B accept.

    Returns (match_id, chat_id). We derive chat_id from the match list.
    """
    user_b_id = await _get_my_id(client, token_b)

    # A sends match request
    resp = await client.post(
        f"/api/v1/matches/request/{user_b_id}",
        headers=_auth_header(token_a),
    )
    match_id = resp.json()["data"]["id"]

    # B accepts
    await client.post(
        f"/api/v1/matches/{match_id}/action",
        headers=_auth_header(token_b),
        json={"action": "accept"},
    )

    # Get the chat_id from A's chat list
    resp = await client.get("/api/v1/chats", headers=_auth_header(token_a))
    chats = resp.json()["data"]["items"]
    chat_id = chats[0]["id"] if chats else None

    return match_id, chat_id


def _make_pass_decision() -> ModerationDecision:
    """Return a 'pass' moderation decision."""
    return ModerationDecision(
        result=ModerationResult(
            is_violation=False,
            violation_type="none",
            confidence=0.95,
            reason="正常消息",
            suggestion="pass",
        ),
        action="pass",
    )


# ===== Tests =====


class TestListChats:
    """Tests for GET /chats."""

    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        """New user has no chats."""
        token = await _register_and_login(client, "nochats", "nochats@test.com")
        resp = await client.get("/api/v1/chats", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_list_with_chat(self, client: AsyncClient):
        """After a match is accepted, both users see the chat."""
        token_a = await _register_and_login(client, "chat_a", "chat_a@test.com")
        token_b = await _register_and_login(client, "chat_b", "chat_b@test.com")
        await _create_accepted_match(client, token_a, token_b)

        # User A should see 1 chat
        resp = await client.get("/api/v1/chats", headers=_auth_header(token_a))
        data = resp.json()
        assert data["data"]["total"] == 1
        chat = data["data"]["items"][0]
        assert chat["other_user_nickname"] is not None
        assert "unread_count" in chat

    @pytest.mark.asyncio
    async def test_list_no_auth(self, client: AsyncClient):
        """Chat list requires authentication."""
        resp = await client.get("/api/v1/chats")
        assert resp.status_code == 422


class TestSendMessage:
    """Tests for POST /chats/{chat_id}/messages."""

    @pytest.mark.asyncio
    async def test_send_text_message(self, client: AsyncClient):
        """Can send a text message in an existing chat."""
        token_a = await _register_and_login(client, "msg_a", "msg_a@test.com")
        token_b = await _register_and_login(client, "msg_b", "msg_b@test.com")
        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        with patch(
            "app.services.chat_service.moderate_content",
            return_value=_make_pass_decision(),
        ):
            resp = await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "你好，一起学习吗？", "content_type": "text"},
                headers=_auth_header(token_a),
            )

        assert resp.status_code == 201
        data = resp.json()
        assert data["data"]["content"] == "你好，一起学习吗？"
        assert data["data"]["content_type"] == "text"
        assert data["data"]["sender_id"] == await _get_my_id(client, token_a)

    @pytest.mark.asyncio
    async def test_send_message_not_participant(self, client: AsyncClient):
        """Cannot send message in a chat you don't belong to."""
        token_a = await _register_and_login(client, "nope_a", "nope_a@test.com")
        token_b = await _register_and_login(client, "nope_b", "nope_b@test.com")
        token_c = await _register_and_login(client, "nope_c", "nope_c@test.com")

        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        # User C tries to send — should fail
        with patch(
            "app.services.chat_service.moderate_content",
            return_value=_make_pass_decision(),
        ):
            resp = await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "spy message", "content_type": "text"},
                headers=_auth_header(token_c),
            )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_no_auth(self, client: AsyncClient):
        """Sending a message requires auth."""
        resp = await client.post(
            "/api/v1/chats/1/messages",
            json={"content": "test", "content_type": "text"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_send_message_blocked_by_moderation(self, client: AsyncClient):
        """Message blocked by AI moderation returns 400."""
        token_a = await _register_and_login(client, "mod_a", "mod_a@test.com")
        token_b = await _register_and_login(client, "mod_b", "mod_b@test.com")
        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        block_decision = ModerationDecision(
            result=ModerationResult(
                is_violation=True,
                violation_type="spam",
                confidence=0.9,
                reason="垃圾广告",
                suggestion="block",
            ),
            action="block",
        )
        with patch(
            "app.services.chat_service.moderate_content",
            return_value=block_decision,
        ):
            resp = await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "加我微信xxx", "content_type": "text"},
                headers=_auth_header(token_a),
            )
        assert resp.status_code == 400


class TestGetMessages:
    """Tests for GET /chats/{chat_id}/messages."""

    @pytest.mark.asyncio
    async def test_get_empty_history(self, client: AsyncClient):
        """New chat has no messages."""
        token_a = await _register_and_login(client, "hist_a", "hist_a@test.com")
        token_b = await _register_and_login(client, "hist_b", "hist_b@test.com")
        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        resp = await client.get(
            f"/api/v1/chats/{chat_id}/messages",
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_get_history_with_messages(self, client: AsyncClient):
        """After sending messages, they appear in history."""
        token_a = await _register_and_login(client, "hist2_a", "hist2_a@test.com")
        token_b = await _register_and_login(client, "hist2_b", "hist2_b@test.com")
        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        with patch(
            "app.services.chat_service.moderate_content",
            return_value=_make_pass_decision(),
        ):
            await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "消息1", "content_type": "text"},
                headers=_auth_header(token_a),
            )
            await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "消息2", "content_type": "text"},
                headers=_auth_header(token_a),
            )

        resp = await client.get(
            f"/api/v1/chats/{chat_id}/messages",
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 2
        assert data["data"]["items"][0]["content"] == "消息1"

    @pytest.mark.asyncio
    async def test_get_history_not_participant(self, client: AsyncClient):
        """Cannot read messages in a chat you don't belong to."""
        token_a = await _register_and_login(client, "priv_a", "priv_a@test.com")
        token_b = await _register_and_login(client, "priv_b", "priv_b@test.com")
        token_c = await _register_and_login(client, "priv_c", "priv_c@test.com")
        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        resp = await client.get(
            f"/api/v1/chats/{chat_id}/messages",
            headers=_auth_header(token_c),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_since_id_incremental(self, client: AsyncClient):
        """since_id returns only newer messages."""
        token_a = await _register_and_login(client, "since_a", "since_a@test.com")
        token_b = await _register_and_login(client, "since_b", "since_b@test.com")
        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        with patch(
            "app.services.chat_service.moderate_content",
            return_value=_make_pass_decision(),
        ):
            r1 = await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "消息1", "content_type": "text"},
                headers=_auth_header(token_a),
            )
            msg1_id = r1.json()["data"]["id"]

            await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "消息2", "content_type": "text"},
                headers=_auth_header(token_a),
            )

        # Query with since_id=msg1_id
        resp = await client.get(
            f"/api/v1/chats/{chat_id}/messages",
            params={"since_id": msg1_id},
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["content"] == "消息2"


class TestMarkRead:
    """Tests for POST /chats/{chat_id}/messages/read."""

    @pytest.mark.asyncio
    async def test_mark_read(self, client: AsyncClient):
        """Mark unread messages as read."""
        token_a = await _register_and_login(client, "read_a", "read_a@test.com")
        token_b = await _register_and_login(client, "read_b", "read_b@test.com")
        _, chat_id = await _create_accepted_match(client, token_a, token_b)

        # A sends a message to B
        with patch(
            "app.services.chat_service.moderate_content",
            return_value=_make_pass_decision(),
        ):
            await client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"content": "Hello", "content_type": "text"},
                headers=_auth_header(token_a),
            )

        # B marks it as read
        resp = await client.post(
            f"/api/v1/chats/{chat_id}/messages/read",
            headers=_auth_header(token_b),
        )
        assert resp.status_code == 200
        assert resp.json()["data"] >= 1

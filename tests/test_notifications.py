"""Tests for the Notification module — listing, read marking, batch ops."""

import pytest
from httpx import AsyncClient


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
    resp = await client.get("/api/v1/users/me", headers=_auth_header(token))
    return resp.json()["data"]["id"]


# ===== Tests =====


class TestListNotifications:
    """Tests for GET /notifications."""

    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        """New user has no notifications."""
        token = await _register_and_login(client, "nonotifs", "nonotifs@test.com")
        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token)
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 0
        assert data["data"]["unread_count"] == 0

    @pytest.mark.asyncio
    async def test_list_with_notifications(self, client: AsyncClient):
        """After a match request, the target user gets a notification."""
        token_a = await _register_and_login(client, "notif_a", "notif_a@test.com")
        token_b = await _register_and_login(client, "notif_b", "notif_b@test.com")
        user_b_id = await _get_my_id(client, token_b)

        # A requests match with B → B gets a notification
        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )

        # B should see 1 notification
        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token_b)
        )
        data = resp.json()
        assert data["data"]["total"] == 1
        assert data["data"]["unread_count"] == 1
        assert data["data"]["items"][0]["is_read"] is False

    @pytest.mark.asyncio
    async def test_filter_unread_only(self, client: AsyncClient):
        """Filter to show only unread notifications."""
        token_a = await _register_and_login(client, "unread_a", "unread_a@test.com")
        token_b = await _register_and_login(client, "unread_b", "unread_b@test.com")
        user_b_id = await _get_my_id(client, token_b)

        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )

        # Unread only
        resp = await client.get(
            "/api/v1/notifications",
            params={"unread_only": True},
            headers=_auth_header(token_b),
        )
        data = resp.json()
        assert data["data"]["total"] == 1

        # Mark all read
        await client.put(
            "/api/v1/notifications/read-all",
            headers=_auth_header(token_b),
        )

        # Unread filter should now return 0
        resp = await client.get(
            "/api/v1/notifications",
            params={"unread_only": True},
            headers=_auth_header(token_b),
        )
        data = resp.json()
        assert data["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_list_no_auth(self, client: AsyncClient):
        """Notification list requires authentication."""
        resp = await client.get("/api/v1/notifications")
        assert resp.status_code == 422


class TestMarkRead:
    """Tests for PUT /notifications/{id}/read."""

    @pytest.mark.asyncio
    async def test_mark_single_read(self, client: AsyncClient):
        """Can mark a single notification as read."""
        token_a = await _register_and_login(client, "mrk_a", "mrk_a@test.com")
        token_b = await _register_and_login(client, "mrk_b", "mrk_b@test.com")
        user_b_id = await _get_my_id(client, token_b)

        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )

        # Get the notification ID
        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token_b)
        )
        notif_id = resp.json()["data"]["items"][0]["id"]

        # Mark it read
        resp = await client.put(
            f"/api/v1/notifications/{notif_id}/read",
            headers=_auth_header(token_b),
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_read"] is True

    @pytest.mark.asyncio
    async def test_mark_not_owned(self, client: AsyncClient):
        """Cannot mark another user's notification as read."""
        token_a = await _register_and_login(client, "ownr_a", "ownr_a@test.com")
        token_b = await _register_and_login(client, "ownr_b", "ownr_b@test.com")
        token_c = await _register_and_login(client, "ownr_c", "ownr_c@test.com")
        user_b_id = await _get_my_id(client, token_b)

        # A requests match with B → B gets notification
        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )

        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token_b)
        )
        notif_id = resp.json()["data"]["items"][0]["id"]

        # C tries to mark B's notification — should fail
        resp = await client.put(
            f"/api/v1/notifications/{notif_id}/read",
            headers=_auth_header(token_c),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_mark_nonexistent(self, client: AsyncClient):
        """Marking a non-existent notification returns 404."""
        token = await _register_and_login(client, "ghst_n", "ghst_n@test.com")
        resp = await client.put(
            "/api/v1/notifications/99999/read",
            headers=_auth_header(token),
        )
        assert resp.status_code == 404


class TestMarkAllRead:
    """Tests for PUT /notifications/read-all."""

    @pytest.mark.asyncio
    async def test_mark_all_read(self, client: AsyncClient):
        """Can mark all notifications as read."""
        token_a = await _register_and_login(client, "allr_a", "allr_a@test.com")
        token_b = await _register_and_login(client, "allr_b", "allr_b@test.com")
        user_b_id = await _get_my_id(client, token_b)

        # Send 2 match requests to generate 2 notifications for B
        token_c = await _register_and_login(client, "allr_c", "allr_c@test.com")
        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )
        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_c),
        )

        # Verify 2 unread
        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token_b)
        )
        assert resp.json()["data"]["unread_count"] == 2

        # Mark all read
        resp = await client.put(
            "/api/v1/notifications/read-all",
            headers=_auth_header(token_b),
        )
        assert resp.status_code == 200
        assert resp.json()["data"] == 2

        # Verify all read
        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token_b)
        )
        assert resp.json()["data"]["unread_count"] == 0

    @pytest.mark.asyncio
    async def test_mark_all_read_no_auth(self, client: AsyncClient):
        """Requires authentication."""
        resp = await client.put("/api/v1/notifications/read-all")
        assert resp.status_code == 422


class TestBatchRead:
    """Tests for PUT /notifications/batch-read."""

    @pytest.mark.asyncio
    async def test_batch_read(self, client: AsyncClient):
        """Can mark a batch of notifications as read."""
        token_a = await _register_and_login(client, "bat_a", "bat_a@test.com")
        token_b = await _register_and_login(client, "bat_b", "bat_b@test.com")
        user_b_id = await _get_my_id(client, token_b)

        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )

        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token_b)
        )
        items = resp.json()["data"]["items"]
        ids = [it["id"] for it in items if not it["is_read"]]

        # Batch mark
        resp = await client.put(
            "/api/v1/notifications/batch-read",
            json={"ids": ids},
            headers=_auth_header(token_b),
        )
        assert resp.status_code == 200
        assert resp.json()["data"] == len(ids)

    @pytest.mark.asyncio
    async def test_batch_read_includes_others_notif(self, client: AsyncClient):
        """Batch read silently skips notifications owned by other users."""
        token_a = await _register_and_login(client, "bx_a", "bx_a@test.com")
        token_b = await _register_and_login(client, "bx_b", "bx_b@test.com")
        user_b_id = await _get_my_id(client, token_b)

        # A requests match → B gets notification
        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )

        resp = await client.get(
            "/api/v1/notifications", headers=_auth_header(token_b)
        )
        b_notif_id = resp.json()["data"]["items"][0]["id"]

        # A tries batch read including B's notification — should silently skip
        resp = await client.put(
            "/api/v1/notifications/batch-read",
            json={"ids": [b_notif_id]},
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 200
        # A marked 0 of B's notifications
        assert resp.json()["data"] == 0

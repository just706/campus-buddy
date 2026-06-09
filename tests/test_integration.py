"""End-to-end integration tests for the Campus Buddy backend.

Covers the full user journey (register → post → match → chat → notify),
error handling (401/404/409/422/500), and pagination.
AI calls are mocked to avoid external API dependencies.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.ai.matching import MatchResult


# ===== Helpers =====


async def _register_and_login(
    client: AsyncClient,
    username: str,
    email: str,
    university: str = "测试大学",
    nickname: str = "",
) -> str:
    """Register a user and return an access token."""
    await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": "test123456",
        "university": university,
        "nickname": nickname or username,
    })
    resp = await client.post("/api/v1/auth/login", json={
        "login": username,
        "password": "test123456",
    })
    return resp.json()["data"]["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ===== Full User Journey =====


class TestFullUserJourney:
    """End-to-end: register, post, match, chat, notifications."""

    @pytest.mark.asyncio
    async def test_complete_flow(self, client: AsyncClient):
        """
        Full user journey:
        1. Alice registers and logs in
        2. Bob registers and logs in
        3. Alice creates a buddy-finding post
        4. Bob browses posts and finds Alice's post
        5. Alice gets AI recommendations (mocked)
        6. Bob sends a match request to Alice
        7. Alice accepts the match → chat created automatically
        8. Bob sends a message in the chat
        9. Alice checks her notifications
        """
        # ---- Step 1: Alice registers and logs in ----
        token_a = await _register_and_login(
            client, "journey_alice", "journey_alice@test.com",
            university="Tsinghua", nickname="Alice",
        )
        # Get Alice's profile
        resp = await client.get("/api/v1/users/me", headers=_auth(token_a))
        assert resp.status_code == 200
        alice_id = resp.json()["data"]["id"]

        # ---- Step 2: Bob registers and logs in ----
        token_b = await _register_and_login(
            client, "journey_bob", "journey_bob@test.com",
            university="Peking", nickname="Bob",
        )
        resp = await client.get("/api/v1/users/me", headers=_auth(token_b))
        assert resp.status_code == 200
        bob_id = resp.json()["data"]["id"]

        # ---- Step 3: Alice creates a buddy-finding post ----
        resp = await client.post(
            "/api/v1/posts",
            headers=_auth(token_a),
            json={
                "title": "Looking for a study buddy",
                "description": "Preparing for finals at the library.",
                "category": "study",
                "tags": ["Finals", "Library", "Study"],
                "target_count": 1,
                "location": "Main Library",
                "time_range": "Weekday evenings",
            },
        )
        assert resp.status_code == 201
        post_data = resp.json()
        assert post_data["data"]["title"] == "Looking for a study buddy"
        assert post_data["data"]["category"] == "study"
        post_id = post_data["data"]["id"]

        # ---- Step 4: Bob browses posts and finds Alice's ----
        resp = await client.get("/api/v1/posts", headers=_auth(token_b))
        assert resp.status_code == 200
        posts = resp.json()["data"]
        assert posts["total"] >= 1
        titles = [p["title"] for p in posts["items"]]
        assert "Looking for a study buddy" in titles

        # ---- Step 5: Alice gets AI recommendations (mocked) ----
        mock_matches = [
            MatchResult(
                candidate_user_id=bob_id,
                match_score=92.0,
                reason="你们都热爱学习，有共同的学术兴趣。",
            )
        ]
        with patch(
            "app.services.match_service.recommend",
            new_callable=AsyncMock,
            return_value=mock_matches,
        ):
            resp = await client.get(
                "/api/v1/matches/recommendations",
                headers=_auth(token_a),
            )
            assert resp.status_code == 200
            recs = resp.json()["data"]["recommendations"]
            assert len(recs) == 1
            assert recs[0]["match_score"] == 92.0
            assert len(recs[0]["ai_reason"]) > 0

        # ---- Step 6: Bob sends a match request to Alice ----
        resp = await client.post(
            f"/api/v1/matches/request/{alice_id}",
            headers=_auth(token_b),
            json={"post_id": post_id},
        )
        assert resp.status_code == 201
        match_data = resp.json()
        assert match_data["data"]["status"] == "pending"
        match_id = match_data["data"]["id"]

        # ---- Step 7: Alice accepts the match ----
        resp = await client.post(
            f"/api/v1/matches/{match_id}/action",
            headers=_auth(token_a),
            json={"action": "accept"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "accepted"

        # After acceptance, a chat should be created automatically
        resp = await client.get("/api/v1/chats", headers=_auth(token_a))
        assert resp.status_code == 200
        chats = resp.json()["data"]
        assert chats["total"] >= 1
        chat_id = chats["items"][0]["id"]

        # ---- Step 8: Bob sends a message in the chat ----
        resp = await client.post(
            f"/api/v1/chats/{chat_id}/messages",
            headers=_auth(token_b),
            json={"content": "Hi Alice! Let's study together.", "content_type": "text"},
        )
        assert resp.status_code == 201
        msg_data = resp.json()
        assert msg_data["data"]["content"] == "Hi Alice! Let's study together."
        assert msg_data["data"]["content_type"] == "text"

        # Alice reads the message
        resp = await client.get(
            f"/api/v1/chats/{chat_id}/messages",
            headers=_auth(token_a),
        )
        assert resp.status_code == 200
        messages = resp.json()["data"]
        assert messages["total"] >= 1
        assert messages["items"][0]["content"] == "Hi Alice! Let's study together."

        # ---- Step 9: Alice checks her notifications ----
        resp = await client.get(
            "/api/v1/notifications",
            headers=_auth(token_a),
        )
        assert resp.status_code == 200
        notifs = resp.json()["data"]
        # Alice should have at least the "match success" notification
        assert notifs["total"] >= 1
        notif_types = [n["type"] for n in notifs["items"]]
        assert "match" in notif_types


# ===== Error Handling =====


class TestErrorHandling:
    """Global error handler tests — consistent JSON error responses."""

    @pytest.mark.asyncio
    async def test_401_unauthenticated(self, client: AsyncClient):
        """Protected endpoints return 401 without valid auth."""
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 422  # FastAPI: missing required header

        resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert resp.status_code == 401
        body = resp.json()
        assert body["code"] == 401
        assert body["data"] is None

    @pytest.mark.asyncio
    async def test_404_not_found(self, client: AsyncClient):
        """Non-existent resources return 404."""
        token = await _register_and_login(client, "nf_user", "nf@test.com")

        # Non-existent post
        resp = await client.get("/api/v1/posts/99999", headers=_auth(token))
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == 404
        assert body["data"] is None

        # Non-existent match
        resp = await client.post(
            "/api/v1/matches/99999/action",
            headers=_auth(token),
            json={"action": "accept"},
        )
        assert resp.status_code == 404
        assert resp.json()["code"] == 404

    @pytest.mark.asyncio
    async def test_409_conflict_duplicate_registration(self, client: AsyncClient):
        """Duplicate username/email returns 409."""
        await _register_and_login(client, "dup_user", "dup@test.com")

        # Try registering with the same username
        resp = await client.post("/api/v1/auth/register", json={
            "username": "dup_user",
            "email": "other@test.com",
            "password": "123456",
            "university": "Tsinghua",
        })
        assert resp.status_code == 409
        assert resp.json()["code"] == 409
        assert resp.json()["data"] is None

    @pytest.mark.asyncio
    async def test_400_bad_request(self, client: AsyncClient):
        """Invalid input returns appropriate error."""
        token = await _register_and_login(client, "br_user", "br@test.com")

        # Try to match with yourself
        resp = await client.get("/api/v1/users/me", headers=_auth(token))
        my_id = resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/matches/request/{my_id}",
            headers=_auth(token),
        )
        assert resp.status_code == 400
        assert resp.json()["code"] == 400

    @pytest.mark.asyncio
    async def test_404_for_unknown_route(self, client: AsyncClient):
        """Unknown endpoints return 404 with APIResponse format."""
        resp = await client.get("/api/v1/nonexistent")
        assert resp.status_code == 404
        body = resp.json()
        assert body["code"] == 404
        assert body["data"] is None

    @pytest.mark.asyncio
    async def test_422_validation_error(self, client: AsyncClient):
        """Invalid request body returns 422 with readable message."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "x"},  # Missing required fields
        )
        assert resp.status_code == 422
        body = resp.json()
        assert body["code"] == 422
        assert body["data"] is None
        # The message should mention the missing fields
        assert len(body["message"]) > 0


# ===== Pagination =====


class TestPagination:
    """Pagination works correctly across list endpoints."""

    @pytest.mark.asyncio
    async def test_posts_pagination(self, client: AsyncClient):
        """Post listing supports pagination with correct total and page info."""
        token = await _register_and_login(client, "page_user", "page@test.com")

        # Create 5 posts
        for i in range(5):
            await client.post(
                "/api/v1/posts",
                headers=_auth(token),
                json={
                    "title": f"Test Post {i}",
                    "description": f"Description {i}",
                    "category": "other",
                    "tags": ["test"],
                },
            )

        # Page 1: 3 items per page
        resp = await client.get(
            "/api/v1/posts?page=1&page_size=3",
            headers=_auth(token),
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 3
        assert len(data["items"]) == 3

        # Page 2: remaining 2 items
        resp = await client.get(
            "/api/v1/posts?page=2&page_size=3",
            headers=_auth(token),
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 5
        assert data["page"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_posts_filter_by_category(self, client: AsyncClient):
        """Post listing can filter by category."""
        token = await _register_and_login(client, "cat_user", "cat@test.com")

        await client.post(
            "/api/v1/posts",
            headers=_auth(token),
            json={
                "title": "Study Post",
                "description": "Study together",
                "category": "study",
                "tags": ["study"],
            },
        )
        await client.post(
            "/api/v1/posts",
            headers=_auth(token),
            json={
                "title": "Sports Post",
                "description": "Play badminton",
                "category": "sports",
                "tags": ["sports"],
            },
        )

        # Filter by study category
        resp = await client.get(
            "/api/v1/posts?category=study",
            headers=_auth(token),
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 1
        assert data["items"][0]["category"] == "study"

    @pytest.mark.asyncio
    async def test_notifications_pagination(self, client: AsyncClient):
        """Notification listing supports pagination."""
        # Register two users, create a match, and accept it to generate notifications
        token_a = await _register_and_login(client, "notif_a", "notif_a@test.com")
        token_b = await _register_and_login(client, "notif_b", "notif_b@test.com")

        resp = await client.get("/api/v1/users/me", headers=_auth(token_a))
        user_a_id = resp.json()["data"]["id"]

        # B sends match to A
        resp = await client.post(
            f"/api/v1/matches/request/{user_a_id}",
            headers=_auth(token_b),
        )
        match_id = resp.json()["data"]["id"]

        # A accepts (generates notifications)
        await client.post(
            f"/api/v1/matches/{match_id}/action",
            headers=_auth(token_a),
            json={"action": "accept"},
        )

        # Check pagination on notifications
        resp = await client.get(
            "/api/v1/notifications?page=1&page_size=10",
            headers=_auth(token_a),
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] >= 1
        assert data["page"] == 1


# ===== Health Check =====


class TestHealthCheck:
    """Health check and root endpoint tests."""

    @pytest.mark.asyncio
    async def test_root_health_check(self, client: AsyncClient):
        """GET / returns app info."""
        resp = await client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["app"] == "CampusBuddy"
        assert body["status"] == "running"

    @pytest.mark.asyncio
    async def test_swagger_docs_accessible(self, client: AsyncClient):
        """Swagger docs are accessible."""
        resp = await client.get("/docs")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_schema(self, client: AsyncClient):
        """OpenAPI schema is generated correctly."""
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "paths" in schema
        # Verify tag metadata is present
        tags = {t["name"]: t for t in schema.get("tags", [])}
        assert "health" in tags
        assert "auth" in tags
        assert "users" in tags
        assert "posts" in tags
        assert "matches" in tags
        assert "chats" in tags
        assert "notifications" in tags

"""Tests for the Match module — requests, acceptance, rejection, and listing.

AI matching calls are mocked to avoid external API dependencies.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.ai.matching import MatchResult, MatchResultList
from app.core.security import create_access_token


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


# ===== Mock AI Recommendation Results =====


def _make_mock_recommendations(candidate_ids: list[int]) -> list[MatchResult]:
    """Build a list of MatchResult objects for testing."""
    return [
        MatchResult(
            candidate_user_id=cid,
            match_score=85.0 - i * 10,
            reason=f"你们有共同的兴趣爱好，都是{cid}号用户的好搭子",
        )
        for i, cid in enumerate(candidate_ids)
    ]


# ===== Tests =====


class TestRequestMatch:
    """Tests for POST /matches/request/{target_user_id}."""

    @pytest.mark.asyncio
    async def test_request_match_success(self, client: AsyncClient):
        """A user can send a match request to another user."""
        token_a = await _register_and_login(client, "req_user_a", "req_a@test.com")
        token_b = await _register_and_login(client, "req_user_b", "req_b@test.com")

        # We need user_b's ID. Get it from the /users/me endpoint.
        resp = await client.get("/api/v1/users/me", headers=_auth_header(token_b))
        user_b_id = resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == 201
        assert data["data"]["status"] == "pending"
        assert data["data"]["target_user_id"] == user_b_id

    @pytest.mark.asyncio
    async def test_request_match_self(self, client: AsyncClient):
        """Cannot match with yourself."""
        token = await _register_and_login(client, "self_matcher", "selfmatch@test.com")
        resp = await client.get("/api/v1/users/me", headers=_auth_header(token))
        my_id = resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/matches/request/{my_id}",
            headers=_auth_header(token),
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_request_match_duplicate(self, client: AsyncClient):
        """Cannot send a duplicate match request."""
        token_a = await _register_and_login(client, "dup_a", "dup_a@test.com")
        token_b = await _register_and_login(client, "dup_b", "dup_b@test.com")

        resp = await client.get("/api/v1/users/me", headers=_auth_header(token_b))
        user_b_id = resp.json()["data"]["id"]

        # First request
        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )
        # Second request — should fail
        resp = await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_request_match_no_auth(self, client: AsyncClient):
        """Match request without auth should fail."""
        resp = await client.post("/api/v1/matches/request/1")
        assert resp.status_code == 422  # Missing header

    @pytest.mark.asyncio
    async def test_request_match_nonexistent_user(self, client: AsyncClient):
        """Requesting match with non-existent user returns 404."""
        token = await _register_and_login(client, "ghost_hunter", "ghost@test.com")
        resp = await client.post(
            "/api/v1/matches/request/99999",
            headers=_auth_header(token),
        )
        assert resp.status_code == 404


class TestHandleMatchAction:
    """Tests for POST /matches/{match_id}/action."""

    @pytest.mark.asyncio
    async def test_accept_match(self, client: AsyncClient):
        """Target user can accept a pending match."""
        token_a = await _register_and_login(client, "acc_a", "acc_a@test.com")
        token_b = await _register_and_login(client, "acc_b", "acc_b@test.com")

        resp = await client.get("/api/v1/users/me", headers=_auth_header(token_b))
        user_b_id = resp.json()["data"]["id"]

        # A requests match with B
        resp = await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )
        match_id = resp.json()["data"]["id"]

        # B accepts
        resp = await client.post(
            f"/api/v1/matches/{match_id}/action",
            headers=_auth_header(token_b),
            json={"action": "accept"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_reject_match(self, client: AsyncClient):
        """Target user can reject a pending match."""
        token_a = await _register_and_login(client, "rej_a", "rej_a@test.com")
        token_b = await _register_and_login(client, "rej_b", "rej_b@test.com")

        resp = await client.get("/api/v1/users/me", headers=_auth_header(token_b))
        user_b_id = resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )
        match_id = resp.json()["data"]["id"]

        # B rejects
        resp = await client.post(
            f"/api/v1/matches/{match_id}/action",
            headers=_auth_header(token_b),
            json={"action": "reject"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_accept_not_target_user(self, client: AsyncClient):
        """Only the target user can accept/reject a match."""
        token_a = await _register_and_login(client, "notarg_a", "notarg_a@test.com")
        token_b = await _register_and_login(client, "notarg_b", "notarg_b@test.com")
        token_c = await _register_and_login(client, "notarg_c", "notarg_c@test.com")

        resp = await client.get("/api/v1/users/me", headers=_auth_header(token_b))
        user_b_id = resp.json()["data"]["id"]

        resp = await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )
        match_id = resp.json()["data"]["id"]

        # C tries to accept — should fail
        resp = await client.post(
            f"/api/v1/matches/{match_id}/action",
            headers=_auth_header(token_c),
            json={"action": "accept"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_accept_already_processed(self, client: AsyncClient):
        """Cannot accept a match that is already accepted/rejected."""
        token_a = await _register_and_login(client, "done_a", "done_a@test.com")
        token_b = await _register_and_login(client, "done_b", "done_b@test.com")

        resp = await client.get("/api/v1/users/me", headers=_auth_header(token_b))
        user_b_id = resp.json()["data"]["id"]

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
        # B tries to accept again
        resp = await client.post(
            f"/api/v1/matches/{match_id}/action",
            headers=_auth_header(token_b),
            json={"action": "accept"},
        )
        assert resp.status_code == 400


class TestListMatches:
    """Tests for GET /matches."""

    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        """New user has no matches."""
        token = await _register_and_login(client, "nomatches", "nomatches@test.com")
        resp = await client.get("/api/v1/matches", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    @pytest.mark.asyncio
    async def test_list_with_matches(self, client: AsyncClient):
        """User can see their matches."""
        token_a = await _register_and_login(client, "list_a", "list_a@test.com")
        token_b = await _register_and_login(client, "list_b", "list_b@test.com")

        resp = await client.get("/api/v1/users/me", headers=_auth_header(token_b))
        user_b_id = resp.json()["data"]["id"]

        # A sends request to B
        await client.post(
            f"/api/v1/matches/request/{user_b_id}",
            headers=_auth_header(token_a),
        )

        # A should see 1 match
        resp = await client.get("/api/v1/matches", headers=_auth_header(token_a))
        data = resp.json()
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_no_auth(self, client: AsyncClient):
        """Match list requires authentication."""
        resp = await client.get("/api/v1/matches")
        assert resp.status_code == 422


class TestRecommendations:
    """Tests for GET /matches/recommendations (AI-powered)."""

    @pytest.mark.asyncio
    async def test_recommendations_no_candidates(self, client: AsyncClient):
        """When there are no other users, recommendations return empty."""
        token = await _register_and_login(client, "lone_user", "lone@test.com")

        resp = await client.get(
            "/api/v1/matches/recommendations",
            headers=_auth_header(token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] == 0

    @pytest.mark.asyncio
    async def test_recommendations_with_candidates(self, client: AsyncClient):
        """AI recommendations return scored candidates."""
        token_a = await _register_and_login(client, "rec_a", "rec_a@test.com")
        # Create candidate users
        await _register_and_login(client, "rec_b", "rec_b@test.com")
        await _register_and_login(client, "rec_c", "rec_c@test.com")

        # Build mock candidates to return from the mocked recommend()
        mock_matches = _make_mock_recommendations([2, 3])

        with patch(
            "app.services.match_service.recommend",
            new_callable=AsyncMock,
            return_value=mock_matches,
        ):
            resp = await client.get(
                "/api/v1/matches/recommendations",
                headers=_auth_header(token_a),
            )

        assert resp.status_code == 200
        data = resp.json()
        recs = data["data"]["recommendations"]
        assert len(recs) == 2
        assert recs[0]["match_score"] == 85.0
        assert len(recs[0]["ai_reason"]) > 0

    @pytest.mark.asyncio
    async def test_recommendations_no_auth(self, client: AsyncClient):
        """Recommendations require authentication."""
        resp = await client.get("/api/v1/matches/recommendations")
        assert resp.status_code == 422

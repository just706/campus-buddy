"""Tests for user profile endpoints."""

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    """Helper: register a user and return an access token."""
    await client.post("/api/v1/auth/register", json={
        "username": "profiletest",
        "email": "profile@campus.edu",
        "password": "123456",
        "university": "Tsinghua",
        "nickname": "Profiler",
        "gender": "male",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "login": "profiletest",
        "password": "123456",
    })
    return resp.json()["data"]["access_token"]


class TestGetProfile:
    """GET /users/me tests."""

    @pytest.mark.asyncio
    async def test_get_profile_authenticated(self, client: AsyncClient):
        """Authenticated user can fetch their profile."""
        token = await _register_and_login(client)
        resp = await client.get("/api/v1/users/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == "profiletest"
        assert data["nickname"] == "Profiler"

    @pytest.mark.asyncio
    async def test_get_profile_no_auth(self, client: AsyncClient):
        """Request without auth header returns 422 (missing header)."""
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_profile_invalid_token(self, client: AsyncClient):
        """Request with a malformed token returns 401."""
        resp = await client.get("/api/v1/users/me", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        assert resp.status_code == 401


class TestUpdateProfile:
    """PUT /users/me tests."""

    @pytest.mark.asyncio
    async def test_update_bio_and_tags(self, client: AsyncClient):
        """Update bio and interest tags."""
        token = await _register_and_login(client)
        resp = await client.put("/api/v1/users/me", headers={
            "Authorization": f"Bearer {token}",
        }, json={
            "bio": "Updated bio",
            "tags": ["Python", "Badminton"],
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["bio"] == "Updated bio"
        assert data["tags"] == ["Python", "Badminton"]

    @pytest.mark.asyncio
    async def test_partial_update(self, client: AsyncClient):
        """Only supplied fields change; others remain."""
        token = await _register_and_login(client)
        resp = await client.put("/api/v1/users/me", headers={
            "Authorization": f"Bearer {token}",
        }, json={
            "nickname": "NewName",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["nickname"] == "NewName"
        assert data["bio"] is None  # unchanged

    @pytest.mark.asyncio
    async def test_update_no_auth(self, client: AsyncClient):
        """Update without auth returns 422."""
        resp = await client.put("/api/v1/users/me", json={"bio": "x"})
        assert resp.status_code == 422

"""Tests for authentication endpoints — register, login, refresh."""

import pytest
from httpx import AsyncClient


class TestRegister:
    """Registration endpoint tests."""

    REGISTER_URL = "/api/v1/auth/register"

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """A valid registration returns 201 with user data."""
        resp = await client.post(self.REGISTER_URL, json={
            "username": "newuser",
            "email": "new@campus.edu",
            "password": "123456",
            "university": "Tsinghua",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == 201
        assert data["data"]["username"] == "newuser"
        assert data["data"]["email"] == "new@campus.edu"
        assert "id" in data["data"]
        assert "hashed_password" not in str(data["data"])

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient):
        """Registering with an existing username returns 409."""
        await client.post(self.REGISTER_URL, json={
            "username": "dup",
            "email": "first@campus.edu",
            "password": "123456",
            "university": "Tsinghua",
        })
        resp = await client.post(self.REGISTER_URL, json={
            "username": "dup",
            "email": "second@campus.edu",
            "password": "123456",
            "university": "PKU",
        })
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_register_missing_required_fields(self, client: AsyncClient):
        """Missing required fields (username, password, university) returns 422."""
        resp = await client.post(self.REGISTER_URL, json={
            "email": "bad@campus.edu",
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Password shorter than 6 chars returns 422."""
        resp = await client.post(self.REGISTER_URL, json={
            "username": "shortpwd",
            "email": "short@campus.edu",
            "password": "12345",
            "university": "Tsinghua",
        })
        assert resp.status_code == 422


class TestLogin:
    """Login endpoint tests."""

    @pytest.mark.asyncio
    async def test_login_with_username(self, client: AsyncClient):
        """Login with username returns tokens."""
        await client.post("/api/v1/auth/register", json={
            "username": "logintest",
            "email": "login@campus.edu",
            "password": "mypassword",
            "university": "Tsinghua",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "login": "logintest",
            "password": "mypassword",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_with_email(self, client: AsyncClient):
        """Login with email returns tokens."""
        await client.post("/api/v1/auth/register", json={
            "username": "emaillogin",
            "email": "email-login@campus.edu",
            "password": "mypassword",
            "university": "Tsinghua",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "login": "email-login@campus.edu",
            "password": "mypassword",
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Login with wrong password returns 401."""
        await client.post("/api/v1/auth/register", json={
            "username": "wrongpwd",
            "email": "wrongpwd@campus.edu",
            "password": "correct",
            "university": "Tsinghua",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "login": "wrongpwd",
            "password": "incorrect",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login with nonexistent credentials returns 401."""
        resp = await client.post("/api/v1/auth/login", json={
            "login": "noone",
            "password": "whatever",
        })
        assert resp.status_code == 401


class TestTokenRefresh:
    """Token refresh endpoint tests."""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient):
        """A valid refresh token returns new tokens."""
        await client.post("/api/v1/auth/register", json={
            "username": "refreshme",
            "email": "refresh@campus.edu",
            "password": "123456",
            "university": "Tsinghua",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "login": "refreshme",
            "password": "123456",
        })
        refresh_token = login_resp.json()["data"]["refresh_token"]

        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 200
        new_data = resp.json()["data"]
        assert "access_token" in new_data
        assert "refresh_token" in new_data

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, client: AsyncClient):
        """An access token cannot be used to refresh."""
        await client.post("/api/v1/auth/register", json={
            "username": "accrefresh",
            "email": "accrefresh@campus.edu",
            "password": "123456",
            "university": "Tsinghua",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "login": "accrefresh",
            "password": "123456",
        })
        access_token = login_resp.json()["data"]["access_token"]

        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": access_token,
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_garbage_token(self, client: AsyncClient):
        """A random string returns 401."""
        resp = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": "not.a.valid.token",
        })
        assert resp.status_code == 401

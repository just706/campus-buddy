"""Tests for post endpoints — CRUD, filtering, pagination, expiry."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> str:
    """Helper: register a user and return an access token."""
    await client.post("/api/v1/auth/register", json={
        "username": "poster",
        "email": "poster@campus.edu",
        "password": "123456",
        "university": "Tsinghua",
        "nickname": "Post Tester",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "login": "poster",
        "password": "123456",
    })
    return resp.json()["data"]["access_token"]


def _auth(token: str) -> dict:
    """Build Authorization header dict for a given token."""
    return {"Authorization": f"Bearer {token}"}


class TestCreatePost:
    """POST /posts tests."""

    @pytest.mark.asyncio
    async def test_create_post_success(self, client: AsyncClient):
        """Create a post returns 201 with post data."""
        token = await _register_and_login(client)
        resp = await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "找学习搭子",
            "description": "一起复习期末",
            "category": "study",
            "tags": ["Python", "期末"],
            "target_count": 3,
            "location": "图书馆",
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["title"] == "找学习搭子"
        assert data["category"] == "study"
        assert data["tags"] == ["Python", "期末"]
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_post_requires_auth(self, client: AsyncClient):
        """Creating a post without auth returns 422."""
        resp = await client.post("/api/v1/posts", json={
            "title": "no auth",
            "category": "study",
        })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_post_missing_category(self, client: AsyncClient):
        """Category is required."""
        token = await _register_and_login(client)
        resp = await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "missing category",
        })
        assert resp.status_code == 422


class TestListPosts:
    """GET /posts tests."""

    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        """List returns empty when no posts exist."""
        token = await _register_and_login(client)
        resp = await client.get("/api/v1/posts", headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_with_posts(self, client: AsyncClient):
        """List returns created posts."""
        token = await _register_and_login(client)
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Post A", "category": "study",
        })
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Post B", "category": "sports",
        })
        resp = await client.get("/api/v1/posts", headers=_auth(token))
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_list_filter_by_category(self, client: AsyncClient):
        """Filter by a single category."""
        token = await _register_and_login(client)
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Study Post", "category": "study",
        })
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Sports Post", "category": "sports",
        })
        resp = await client.get("/api/v1/posts?category=study", headers=_auth(token))
        data = resp.json()["data"]
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Study Post"

    @pytest.mark.asyncio
    async def test_list_filter_by_keyword(self, client: AsyncClient):
        """Search by keyword in title/description."""
        token = await _register_and_login(client)
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Python 学习", "category": "study",
        })
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "羽毛球", "category": "sports",
        })
        resp = await client.get("/api/v1/posts?keyword=Python", headers=_auth(token))
        data = resp.json()["data"]
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_excludes_expired(self, client: AsyncClient):
        """Expired posts are not returned in the list."""
        token = await _register_and_login(client)
        past = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Expired", "category": "study", "expires_at": past,
        })
        await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Active", "category": "study",
        })
        resp = await client.get("/api/v1/posts", headers=_auth(token))
        data = resp.json()["data"]
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Active"


class TestGetPost:
    """GET /posts/{id} tests."""

    @pytest.mark.asyncio
    async def test_get_post(self, client: AsyncClient):
        """Fetch a single post by ID."""
        token = await _register_and_login(client)
        create_resp = await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Target Post", "category": "study",
        })
        post_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/posts/{post_id}", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Target Post"

    @pytest.mark.asyncio
    async def test_get_post_not_found(self, client: AsyncClient):
        """Non-existent post returns 404."""
        token = await _register_and_login(client)
        resp = await client.get("/api/v1/posts/99999", headers=_auth(token))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_post_lazy_expire(self, client: AsyncClient):
        """Accessing an expired post lazily closes it."""
        token = await _register_and_login(client)
        past = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        create_resp = await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Will Expire", "category": "study", "expires_at": past,
        })
        post_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/posts/{post_id}", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "closed"


class TestUpdatePost:
    """PUT /posts/{id} tests."""

    @pytest.mark.asyncio
    async def test_update_own_post(self, client: AsyncClient):
        """Author can update their own post."""
        token = await _register_and_login(client)
        create_resp = await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Old Title", "category": "study",
        })
        post_id = create_resp.json()["data"]["id"]

        resp = await client.put(f"/api/v1/posts/{post_id}", headers=_auth(token), json={
            "title": "New Title",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "New Title"

    @pytest.mark.asyncio
    async def test_update_others_post_forbidden(self, client: AsyncClient):
        """Non-author cannot update someone else's post."""
        token_a = await _register_and_login(client)

        # Register a second user
        await client.post("/api/v1/auth/register", json={
            "username": "otheruser", "email": "other@campus.edu",
            "password": "123456", "university": "PKU",
        })
        login_b = await client.post("/api/v1/auth/login", json={
            "login": "otheruser", "password": "123456",
        })
        token_b = login_b.json()["data"]["access_token"]

        # User A creates a post
        create_resp = await client.post("/api/v1/posts", headers=_auth(token_a), json={
            "title": "A's Post", "category": "study",
        })
        post_id = create_resp.json()["data"]["id"]

        # User B tries to edit it
        resp = await client.put(f"/api/v1/posts/{post_id}", headers=_auth(token_b), json={
            "title": "Stolen",
        })
        assert resp.status_code == 403


class TestClosePost:
    """DELETE /posts/{id} tests."""

    @pytest.mark.asyncio
    async def test_close_own_post(self, client: AsyncClient):
        """Author can close their own post."""
        token = await _register_and_login(client)
        create_resp = await client.post("/api/v1/posts", headers=_auth(token), json={
            "title": "Close Me", "category": "study",
        })
        post_id = create_resp.json()["data"]["id"]

        resp = await client.delete(f"/api/v1/posts/{post_id}", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "closed"

    @pytest.mark.asyncio
    async def test_close_others_post_forbidden(self, client: AsyncClient):
        """Non-author cannot close someone else's post."""
        token_a = await _register_and_login(client)

        await client.post("/api/v1/auth/register", json={
            "username": "closer", "email": "closer@campus.edu",
            "password": "123456", "university": "PKU",
        })
        login_b = await client.post("/api/v1/auth/login", json={
            "login": "closer", "password": "123456",
        })
        token_b = login_b.json()["data"]["access_token"]

        create_resp = await client.post("/api/v1/posts", headers=_auth(token_a), json={
            "title": "A's Post", "category": "study",
        })
        post_id = create_resp.json()["data"]["id"]

        resp = await client.delete(f"/api/v1/posts/{post_id}", headers=_auth(token_b))
        assert resp.status_code == 403

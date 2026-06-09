"""Tests for the AI content moderation module.

Unit tests for moderation_service grading logic and integration tests
for post creation with mocked moderation.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.ai.moderation import ModerationResult
from app.services.moderation_service import ModerationDecision, moderate_content


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


# ===== Unit Tests: Grading Logic =====


class TestModerationGrading:
    """Test the grading thresholds in moderation_service."""

    @pytest.mark.asyncio
    async def test_block_high_confidence_violation(self):
        """High-confidence violation → block."""
        mock_result = ModerationResult(
            is_violation=True,
            violation_type="spam",
            confidence=0.85,
            reason="广告内容",
            suggestion="block",
        )
        with patch(
            "app.services.moderation_service.moderate",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            decision = await moderate_content("buy now!!!", "post body")
            assert decision.action == "block"

    @pytest.mark.asyncio
    async def test_pass_high_confidence_clean(self):
        """High-confidence clean content → pass."""
        mock_result = ModerationResult(
            is_violation=False,
            violation_type="none",
            confidence=0.95,
            reason="正常社交内容",
            suggestion="pass",
        )
        with patch(
            "app.services.moderation_service.moderate",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            decision = await moderate_content("一起学习吧", "post body")
            assert decision.action == "pass"

    @pytest.mark.asyncio
    async def test_flag_medium_confidence(self):
        """Medium confidence (30%-70%) → flag."""
        mock_result = ModerationResult(
            is_violation=True,
            violation_type="harassment",
            confidence=0.5,
            reason="可能含有不当言论",
            suggestion="flag",
        )
        with patch(
            "app.services.moderation_service.moderate",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            decision = await moderate_content("你真是个憨憨", "post body")
            assert decision.action == "flag"

    @pytest.mark.asyncio
    async def test_pass_low_confidence(self):
        """Low confidence (<30%) → pass regardless of is_violation."""
        mock_result = ModerationResult(
            is_violation=True,
            violation_type="other",
            confidence=0.25,
            reason="不确定是否违规",
            suggestion="pass",
        )
        with patch(
            "app.services.moderation_service.moderate",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            decision = await moderate_content("某个模糊内容", "post body")
            assert decision.action == "pass"

    @pytest.mark.asyncio
    async def test_fallback_on_exception(self):
        """AI call failure → pass (safe default)."""
        with patch(
            "app.services.moderation_service.moderate",
            new_callable=AsyncMock,
            side_effect=Exception("Connection timeout"),
        ):
            decision = await moderate_content("test content", "post body")
            assert decision.action == "pass"
            assert decision.result.confidence == 0.0


# ===== Integration Tests =====


class TestPostModerationIntegration:
    """Test that post creation integrates with moderation."""

    @pytest.mark.asyncio
    async def test_create_post_passes_moderation(self, client: AsyncClient):
        """Post is created when moderation passes."""
        token = await _register_and_login(client, "mod_pass", "mod_pass@test.com")

        mock_result = ModerationResult(
            is_violation=False,
            violation_type="none",
            confidence=0.9,
            reason="正常内容",
            suggestion="pass",
        )
        with patch(
            "app.services.post_service.moderate_content",
            return_value=ModerationDecision(result=mock_result, action="pass"),
        ):
            resp = await client.post(
                "/api/v1/posts",
                json={
                    "title": "找学习搭子",
                    "description": "期末一起复习",
                    "category": "study",
                },
                headers=_auth_header(token),
            )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_create_post_blocked_by_moderation(self, client: AsyncClient):
        """Post is rejected when moderation blocks it."""
        token = await _register_and_login(client, "mod_block", "mod_block@test.com")

        mock_result = ModerationResult(
            is_violation=True,
            violation_type="spam",
            confidence=0.9,
            reason="垃圾广告",
            suggestion="block",
        )
        with patch(
            "app.services.post_service.moderate_content",
            return_value=ModerationDecision(result=mock_result, action="block"),
        ):
            resp = await client.post(
                "/api/v1/posts",
                json={
                    "title": "加我微信 xxx",
                    "description": "免费领取xxx",
                    "category": "other",
                },
                headers=_auth_header(token),
            )
        assert resp.status_code == 400
        assert "violates" in resp.json()["message"].lower()

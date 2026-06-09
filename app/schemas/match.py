"""Match-related Pydantic schemas.

Request/response models for match operations, AI recommendations,
and match request flows.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# ===== API Request Schemas =====


class MatchRequest(BaseModel):
    """Payload for requesting a match with another user."""

    post_id: int | None = Field(default=None, description="Optional post context for the match")


class MatchAction(BaseModel):
    """Payload for accepting or rejecting a pending match."""

    action: str = Field(..., pattern=r"^(accept|reject)$", description="accept or reject")


# ===== API Response Schemas =====


class MatchResponse(BaseModel):
    """Match data returned by the API."""

    id: int
    user_id: int
    target_user_id: int
    post_id: int | None = None
    match_score: float | None = None
    ai_reason: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchedUserBrief(BaseModel):
    """Brief user info embedded in match responses."""

    id: int
    username: str
    nickname: str | None = None
    avatar: str | None = None
    university: str
    gender: str | None = None
    tags: list | None = None

    model_config = {"from_attributes": True}


class MatchDetailResponse(MatchResponse):
    """Match response with embedded user info."""

    user: MatchedUserBrief | None = None
    target_user: MatchedUserBrief | None = None


class MatchListResponse(BaseModel):
    """Paginated match list."""

    items: list[MatchDetailResponse]
    total: int
    page: int
    page_size: int


# ===== AI Recommendation Schemas =====


class RecommendationItem(BaseModel):
    """A single AI recommendation — a user suggested as a potential buddy."""

    user: MatchedUserBrief
    match_score: float = Field(..., ge=0, le=100, description="AI match score (0-100)")
    ai_reason: str = Field(..., description="AI-generated recommendation reason")


class RecommendationResponse(BaseModel):
    """AI-generated list of buddy recommendations."""

    recommendations: list[RecommendationItem]
    total: int

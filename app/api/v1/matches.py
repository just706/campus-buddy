"""Match API endpoints.

AI-powered buddy recommendations, match request/accept/reject flow,
and match history listing.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.match import (
    MatchAction,
    MatchDetailResponse,
    MatchListResponse,
    MatchedUserBrief,
    MatchRequest,
    RecommendationItem,
    RecommendationResponse,
)
from app.services import match_service

router = APIRouter(prefix="/matches")


@router.get(
    "/recommendations",
    response_model=APIResponse[RecommendationResponse],
)
async def get_recommendations(
    limit: int = Query(
        default=10, ge=1, le=50, description="Max candidates to evaluate"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RecommendationResponse]:
    """Get AI-powered buddy recommendations.

    The AI analyzes your profile (school, interests, bio) and finds the
    best matching users among active campus buddies. Returns a ranked
    list with match scores and personalized recommendation reasons.
    """
    ranked = await match_service.get_recommendations(
        db, current_user, limit=limit
    )

    items = [
        RecommendationItem(
            user=MatchedUserBrief.model_validate(user),
            match_score=score,
            ai_reason=reason,
        )
        for user, score, reason in ranked
    ]

    return APIResponse(
        data=RecommendationResponse(
            recommendations=items,
            total=len(items),
        )
    )


@router.post(
    "/request/{target_user_id}",
    response_model=APIResponse[MatchDetailResponse],
    status_code=201,
)
async def request_match(
    target_user_id: int,
    body: MatchRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MatchDetailResponse]:
    """Send a match request to another user.

    The target user will receive a notification and can accept or reject.
    Optionally provide a post_id to indicate which post sparked the request.
    """
    post_id = body.post_id if body else None
    match = await match_service.request_match(
        db, current_user, target_user_id, post_id=post_id
    )
    return APIResponse(
        code=201,
        message="Match request sent",
        data=MatchDetailResponse.model_validate(match),
    )


@router.post(
    "/{match_id}/action",
    response_model=APIResponse[MatchDetailResponse],
)
async def handle_match_action(
    match_id: int,
    body: MatchAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MatchDetailResponse]:
    """Accept or reject a pending match request.

    Only the target user of a pending match can take action.
    On acceptance, a chat session is created automatically.
    """
    match = await match_service.handle_match_action(
        db, match_id, current_user, body.action
    )

    message = "Match accepted" if body.action == "accept" else "Match rejected"
    return APIResponse(
        message=message,
        data=MatchDetailResponse.model_validate(match),
    )


@router.get(
    "",
    response_model=APIResponse[MatchListResponse],
)
async def list_my_matches(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(
        default=None, description="Filter: pending, accepted, rejected"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MatchListResponse]:
    """List my match records (both sent and received).

    Sorted by most recently updated first. Filter by status if desired.
    """
    matches, total = await match_service.get_my_matches(
        db, current_user, page=page, page_size=page_size
    )

    # Collect all related user IDs for batch fetch
    related_ids: set[int] = set()
    for m in matches:
        related_ids.add(m.user_id)
        related_ids.add(m.target_user_id)
    related_ids.discard(current_user.id)

    user_map = await match_service.get_related_user_ids(
        db, list(related_ids)
    )

    items: list[MatchDetailResponse] = []
    for m in matches:
        detail = MatchDetailResponse.model_validate(m)
        detail.user = (
            MatchedUserBrief.model_validate(user_map[m.user_id])
            if m.user_id in user_map
            else None
        )
        detail.target_user = (
            MatchedUserBrief.model_validate(user_map[m.target_user_id])
            if m.target_user_id in user_map
            else None
        )
        items.append(detail)

    # If status filter is provided, filter in Python
    if status:
        items = [it for it in items if it.status == status]
        total = len(items)

    return APIResponse(
        data=MatchListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )

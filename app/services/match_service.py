"""Match business logic.

Handles AI-powered buddy recommendations, match request flows
(request → accept/reject), and match status management.

On match acceptance, a chat session is created atomically.
"""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.matching import MatchResult, recommend
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.chat import Chat
from app.models.match import Match
from app.models.notification import Notification
from app.models.user import User


async def get_recommendations(
    db: AsyncSession,
    current_user: User,
    limit: int = 10,
) -> list[tuple[User, float, str]]:
    """Generate AI-powered buddy recommendations for the current user.

    Excludes the current user and any user who already has a match record
    with them (regardless of status).

    Args:
        db: Async database session.
        current_user: The user requesting recommendations.
        limit: Maximum number of candidates to evaluate (default 10).

    Returns:
        A list of (User, score, reason) tuples sorted by score descending.
    """
    # Find users who already have a match with current_user
    existing_match_subquery = (
        select(Match.target_user_id)
        .where(Match.user_id == current_user.id)
        .union_all(
            select(Match.user_id).where(Match.target_user_id == current_user.id)
        )
    ).subquery()

    # Fetch candidates: active users, not self, not already matched
    query = (
        select(User)
        .where(
            User.id != current_user.id,
            User.is_active == True,  # noqa: E712
            User.id.not_in(select(existing_match_subquery.c[0])),
        )
        .limit(limit)
    )
    result = await db.execute(query)
    candidates = list(result.scalars().all())

    if not candidates:
        return []

    # Call AI matching engine
    ai_results: list[MatchResult] = await recommend(current_user, candidates)

    # Map AI results back to User objects, preserving score order
    candidate_map = {c.id: c for c in candidates}
    ranked: list[tuple[User, float, str]] = []
    for mr in ai_results:
        user = candidate_map.get(mr.candidate_user_id)
        if user is not None:
            ranked.append((user, mr.match_score, mr.reason))

    return ranked


async def request_match(
    db: AsyncSession,
    from_user: User,
    target_user_id: int,
    post_id: int | None = None,
) -> Match:
    """Send a match request from one user to another.

    Args:
        db: Async database session.
        from_user: The user initiating the request.
        target_user_id: The user being requested.
        post_id: Optional post context for the match.

    Returns:
        The newly created pending Match.

    Raises:
        BadRequestException: If trying to match with self.
        NotFoundException: If the target user doesn't exist.
        ConflictException: If a match already exists between these users.
    """
    if target_user_id == from_user.id:
        raise BadRequestException("Cannot match with yourself")

    target = await db.get(User, target_user_id)
    if target is None:
        raise NotFoundException("Target user not found")

    # Check for existing match between the two users (any direction)
    existing = await db.execute(
        select(Match).where(
            or_(
                (Match.user_id == from_user.id)
                & (Match.target_user_id == target_user_id),
                (Match.user_id == target_user_id)
                & (Match.target_user_id == from_user.id),
            )
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("A match already exists between these users")

    match = Match(
        user_id=from_user.id,
        target_user_id=target_user_id,
        post_id=post_id,
        status="pending",
    )
    db.add(match)

    # Notify the target user
    notification = Notification(
        user_id=target_user_id,
        type="match",
        title="新的搭子请求",
        content=f"{from_user.nickname or from_user.username} 想和你成为搭子",
    )
    db.add(notification)

    await db.commit()
    await db.refresh(match)
    return match


async def handle_match_action(
    db: AsyncSession,
    match_id: int,
    current_user: User,
    action: str,
) -> Match:
    """Accept or reject a pending match request.

    Only the target_user of a pending match may accept or reject.
    On acceptance, a Chat session is created atomically and both users
    are notified of the match success.

    Args:
        db: Async database session.
        match_id: The match record ID.
        current_user: The authenticated user performing the action.
        action: 'accept' or 'reject'.

    Returns:
        The updated Match object.

    Raises:
        NotFoundException: If the match doesn't exist.
        ForbiddenException: If the user is not the target_user of this match.
        BadRequestException: If the match is not in 'pending' status.
    """
    match = await db.get(Match, match_id)
    if match is None:
        raise NotFoundException("Match not found")

    if match.target_user_id != current_user.id:
        raise ForbiddenException("Only the target user can accept or reject a match")

    if match.status != "pending":
        raise BadRequestException(f"Match is already {match.status}")

    if action == "accept":
        match.status = "accepted"

        # Create chat session atomically
        chat = Chat(
            match_id=match.id,
            user1_id=match.user_id,
            user2_id=match.target_user_id,
        )
        db.add(chat)

        # Load the requesting user for notification content
        requester = await db.get(User, match.user_id)
        requester_name = (
            requester.nickname or requester.username if requester else "对方"
        )
        acceptor_name = current_user.nickname or current_user.username

        # Notify both users
        notif1 = Notification(
            user_id=match.user_id,
            type="match",
            title="匹配成功！",
            content=f"{acceptor_name} 接受了你的搭子请求，快去聊天吧！",
        )
        notif2 = Notification(
            user_id=match.target_user_id,
            type="match",
            title="匹配成功！",
            content=f"你和 {requester_name} 已经成为搭子，快去聊天吧！",
        )
        db.add(notif1)
        db.add(notif2)

    elif action == "reject":
        match.status = "rejected"

        # Notify the requester
        rejecter_name = current_user.nickname or current_user.username
        notification = Notification(
            user_id=match.user_id,
            type="match",
            title="搭子请求被拒绝",
            content=f"{rejecter_name} 拒绝了你的搭子请求",
        )
        db.add(notification)

    await db.commit()
    await db.refresh(match)
    return match


async def get_my_matches(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Match], int]:
    """List matches for the current user (both sent and received).

    Args:
        db: Async database session.
        current_user: The authenticated user.
        page: Page number (1-indexed).
        page_size: Items per page.

    Returns:
        A tuple of (matches_list, total_count).
    """
    conditions = [
        or_(
            Match.user_id == current_user.id,
            Match.target_user_id == current_user.id,
        )
    ]

    base = select(Match).where(*conditions)

    # Total count
    count_query = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Pagination
    offset = (page - 1) * page_size
    query = (
        base.order_by(Match.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    matches = list(result.scalars().all())

    return matches, total


async def get_related_user_ids(
    db: AsyncSession,
    user_ids: list[int],
) -> dict[int, User]:
    """Batch-fetch user objects by ID list.

    Args:
        db: Async database session.
        user_ids: List of user IDs to fetch.

    Returns:
        A dict mapping user_id → User.
    """
    if not user_ids:
        return {}
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    return {u.id: u for u in result.scalars().all()}

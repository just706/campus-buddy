"""Post business logic.

Handles CRUD operations for buddy-finding posts, including
pagination, filtering, expiry enforcement, ownership checks,
and AI content moderation on creation.
"""

import logging
from datetime import UTC, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.post import Post
from app.schemas.post import PostCreate, PostFilter, PostUpdate
from app.services.moderation_service import moderate_content

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(UTC)


def _is_expired(expires_at: datetime | None) -> bool:
    """Check if a datetime is in the past.

    Normalizes to UTC for comparison since SQLite may return naive
    datetimes that were originally stored as UTC-aware.
    """
    if expires_at is None:
        return False
    # Normalize: if naive, treat as UTC
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < _utcnow()


async def create_post(db: AsyncSession, user_id: int, data: PostCreate) -> Post:
    """Create a new buddy-finding post.

    Runs AI content moderation on the combined title + description before
    persisting. If the content is flagged as a high-confidence violation,
    the post is rejected.

    Args:
        db: Async database session.
        user_id: The ID of the authenticated user creating the post.
        data: Validated post creation payload.

    Returns:
        The newly created Post object.

    Raises:
        BadRequestException: If AI moderation blocks the content.
    """
    # Run AI content moderation on title + description
    content = f"{data.title}\n{data.description}"
    if content.strip():
        decision = await moderate_content(content, context="post body")
        logger.info(
            "Post moderation: action=%s confidence=%.2f type=%s reason=%s",
            decision.action,
            decision.result.confidence,
            decision.result.violation_type,
            decision.result.reason,
        )
        if decision.action == "block":
            raise BadRequestException(
                f"Content violates community guidelines: {decision.result.reason}"
            )

    post = Post(
        user_id=user_id,
        title=data.title,
        description=data.description,
        category=data.category,
        tags=data.tags,
        target_count=data.target_count,
        location=data.location,
        time_range=data.time_range,
        expires_at=data.expires_at,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post(db: AsyncSession, post_id: int) -> Post:
    """Fetch a single post by ID.

    Also enforces expiry: if the post is past expires_at but still
    marked active, it is lazily closed before returning.

    Args:
        db: Async database session.
        post_id: The post's database ID.

    Returns:
        The Post object.

    Raises:
        NotFoundException: If the post does not exist.
    """
    post = await db.get(Post, post_id)
    if post is None:
        raise NotFoundException("Post not found")

    # Lazy-expire: close if past expiry but status not yet updated
    if post.status == "active" and _is_expired(post.expires_at):
        post.status = "closed"
        await db.commit()
        await db.refresh(post)

    return post


async def get_posts(
    db: AsyncSession, filters: PostFilter
) -> tuple[list[Post], int]:
    """List posts with filtering, search, and pagination.

    Expired posts are always excluded from results, regardless of
    whether a background task has updated their status yet.

    Args:
        db: Async database session.
        filters: Category, tag, status, keyword, and pagination params.

    Returns:
        A tuple of (posts_list, total_count).
    """
    conditions = []

    # Hard guard: always exclude expired posts.
    # Use a naive UTC datetime so comparison works correctly with SQLite's
    # timezone-naive column storage.
    naive_utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    conditions.append(
        (Post.expires_at == None)  # noqa: E711
        | (Post.expires_at > naive_utc_now)
    )
    # Only show active posts by default
    conditions.append(Post.status == "active")

    if filters.category:
        conditions.append(Post.category == filters.category)
    if filters.keyword:
        keyword = f"%{filters.keyword}%"
        conditions.append(
            (Post.title.ilike(keyword)) | (Post.description.ilike(keyword))
        )

    base = select(Post).where(*conditions)

    # Total count
    count_query = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # Pagination
    offset = (filters.page - 1) * filters.page_size
    query = (
        base.order_by(Post.created_at.desc())
        .offset(offset)
        .limit(filters.page_size)
    )
    result = await db.execute(query)
    posts = list(result.scalars().all())

    return posts, total


async def update_post(
    db: AsyncSession, post_id: int, user_id: int, data: PostUpdate
) -> Post:
    """Update a post. Only the author may update it.

    Args:
        db: Async database session.
        post_id: The post's database ID.
        user_id: The authenticated user's ID.
        data: Fields to update (partial).

    Returns:
        The updated Post object.

    Raises:
        NotFoundException: If the post does not exist.
        ForbiddenException: If the user is not the post author.
    """
    post = await db.get(Post, post_id)
    if post is None:
        raise NotFoundException("Post not found")
    if post.user_id != user_id:
        raise ForbiddenException("Only the author can edit this post")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


async def close_post(db: AsyncSession, post_id: int, user_id: int) -> Post:
    """Close a post (set status='closed'). Only the author may close.

    Args:
        db: Async database session.
        post_id: The post's database ID.
        user_id: The authenticated user's ID.

    Returns:
        The closed Post object.

    Raises:
        NotFoundException: If the post does not exist.
        ForbiddenException: If the user is not the post author.
    """
    post = await db.get(Post, post_id)
    if post is None:
        raise NotFoundException("Post not found")
    if post.user_id != user_id:
        raise ForbiddenException("Only the author can close this post")

    post.status = "closed"
    await db.commit()
    await db.refresh(post)
    return post

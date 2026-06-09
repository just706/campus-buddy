"""Database initialization utilities.

Provides helpers to create all tables on first run and optionally
seed development data.
"""

import logging

from sqlalchemy import select

from app.db.session import engine, async_session_factory

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Create all database tables defined by ORM models.

    Imports all model modules to ensure they are registered on
    the SQLAlchemy Base metadata before table creation.
    """
    # Import models to register them on Base.metadata
    import app.models.chat  # noqa: F401
    import app.models.match  # noqa: F401
    import app.models.message  # noqa: F401
    import app.models.notification  # noqa: F401
    import app.models.post  # noqa: F401
    import app.models.user  # noqa: F401
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed development data (idempotent — skips if users already exist)
    await seed_db()


async def seed_db() -> None:
    """Populate the database with sample development data.

    Only runs when the user table is empty (first-time setup).
    Creates demo users with different profiles and sample posts
    across various buddy-finding categories.
    """
    from app.core.security import hash_password
    from app.models.user import User
    from app.models.post import Post

    async with async_session_factory() as db:
        # Guard: skip if users already exist
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            logger.debug("Seed data already exists, skipping.")
            return

        logger.info("Seeding development data...")

        # ===== Demo Users =====
        password = hash_password("123456")

        alice = User(
            username="alice",
            email="alice@campus.edu",
            phone="13800001001",
            hashed_password=password,
            university="Tsinghua University",
            college="Computer Science",
            major="Software Engineering",
            grade="Junior",
            nickname="Alice",
            gender="female",
            bio="A coding enthusiast who loves sports and outdoor activities.",
            tags=["Python", "Badminton", "Hiking", "Machine Learning"],
            is_active=True,
            is_verified=True,
        )

        bob = User(
            username="bob",
            email="bob@campus.edu",
            phone="13800001002",
            hashed_password=password,
            university="Peking University",
            college="Business",
            major="Marketing",
            grade="Senior",
            nickname="Bob",
            gender="male",
            bio="Foodie and traveler. Always looking for new restaurants!",
            tags=["Food", "Travel", "Photography", "Basketball"],
            is_active=True,
            is_verified=True,
        )

        charlie = User(
            username="charlie",
            email="charlie@campus.edu",
            phone="13800001003",
            hashed_password=password,
            university="Tsinghua University",
            college="Science",
            major="Physics",
            grade="Sophomore",
            nickname="Charlie",
            gender="male",
            bio="Bookworm who needs a study buddy for finals prep.",
            tags=["Physics", "Math", "Library", "Study"],
            is_active=True,
            is_verified=False,
        )

        db.add_all([alice, bob, charlie])
        await db.flush()  # Flush to populate user IDs

        # ===== Sample Posts =====
        posts = [
            Post(
                user_id=alice.id,
                title="Looking for a badminton partner",
                description="I play at the campus sports center every weekend. Looking for someone at intermediate level or above. Singles or doubles both fine!",
                category="sports",
                tags=["Badminton", "Weekend", "Intermediate"],
                target_count=1,
                current_count=1,
                location="Sports Center Court 3",
                time_range="Weekends 2-5 PM",
                status="active",
            ),
            Post(
                user_id=bob.id,
                title="Hotpot dinner tonight!",
                description="Anyone want to join for hotpot at Haidilao near campus? I'm going at 7pm. Split the bill.",
                category="dining",
                tags=["Hotpot", "Dinner", "Haidilao"],
                target_count=2,
                current_count=1,
                location="Haidilao (near East Gate)",
                time_range="Today 7:00 PM",
                status="active",
            ),
            Post(
                user_id=charlie.id,
                title="Study group for Quantum Mechanics final",
                description="Preparing for the QM final exam. Looking for 2-3 people to form a study group. We'll review past exams and discuss problem sets.",
                category="study",
                tags=["Quantum Mechanics", "Final Exam", "Study Group", "Library"],
                target_count=3,
                current_count=1,
                location="Library Room 302",
                time_range="Weekday evenings 6-9 PM",
                status="active",
            ),
            Post(
                user_id=alice.id,
                title="Weekend hiking at Fragrant Hills",
                description="Planning a day hike this Saturday. The trail is moderate difficulty, about 4 hours round trip. Bring water and snacks!",
                category="travel",
                tags=["Hiking", "Nature", "Weekend", "Outdoor"],
                target_count=4,
                current_count=1,
                location="Fragrant Hills Park",
                time_range="Saturday 8 AM - 2 PM",
                status="active",
            ),
        ]

        db.add_all(posts)
        await db.commit()

        logger.info("Seed data created: 3 users, %d posts", len(posts))

"""Database initialization utilities.

Provides helpers to create all tables on first run and optionally
seed development data.
"""

from app.db.session import engine


async def init_db() -> None:
    """Create all database tables defined by ORM models.

    Imports all model modules to ensure they are registered on
    the SQLAlchemy Base metadata before table creation.
    """
    # Import models to register them on Base.metadata
    import app.models.user  # noqa: F401
    import app.models.notification  # noqa: F401
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

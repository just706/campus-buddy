"""Database session management.

Provides the async SQLAlchemy engine and session factory, along with
a FastAPI dependency for obtaining a database session per request.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    The session is automatically closed when the request finishes.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

"""Alembic environment configuration — async SQLAlchemy + SQLite.

Connects to the database using the URL from app.core.config.settings,
supports both online (direct) and offline (SQL script) migration modes,
and auto-detects schema changes by importing all ORM models.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Alembic Config object (reads alembic.ini)
config = context.config

# Configure Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ===== Import models so Base.metadata is fully populated =====
from app.models.base import Base

# Ensure all models are imported before accessing Base.metadata
import app.models.chat  # noqa: F401
import app.models.match  # noqa: F401
import app.models.message  # noqa: F401
import app.models.notification  # noqa: F401
import app.models.post  # noqa: F401
import app.models.user  # noqa: F401

# Set the metadata target for autogenerate
target_metadata = Base.metadata

# ===== Database URL from application settings =====
from app.core.config import settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (produce SQL scripts).

    This configures the context with just a URL, not an Engine.
    Calls to context.execute() emit SQL to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite-specific: use batch mode for ALTER TABLE
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations on the given synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # SQLite-specific: use batch mode for ALTER TABLE operations
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations in an async context."""
    configuration = config.get_section(config.config_ini_section, {})
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (against a live database).

    Uses an async engine and runs the migration inside an event loop.
    """
    asyncio.run(run_async_migrations())


# ===== Entry point =====
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

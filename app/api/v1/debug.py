"""Debug API endpoints for database inspection.

Provides endpoints to list tables, describe schemas, and query data.
Intended for development/testing only.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.base import Base
from app.models.user import User

router = APIRouter(prefix="/debug")


@router.get("/tables")
async def list_tables(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """List all database tables with row counts and schema info."""
    tables_info = []
    for table_name, table in Base.metadata.tables.items():
        # Row count
        result = await db.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
        count = result.scalar()

        # Columns
        columns = []
        for col in table.columns:
            columns.append({
                "name": col.name,
                "type": str(col.type),
                "nullable": col.nullable,
                "primary_key": col.primary_key,
                "foreign_key": str(list(col.foreign_keys)) if col.foreign_keys else None,
            })

        tables_info.append({
            "name": table_name,
            "row_count": count,
            "columns": columns,
        })

    return {
        "code": 200,
        "message": "ok",
        "data": {"tables": tables_info},
    }


@router.get("/tables/{table_name}")
async def query_table(
    table_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Query a specific table with pagination.

    Returns rows, total count, and column metadata.
    """
    # Validate table exists
    if table_name not in Base.metadata.tables:
        return {
            "code": 404,
            "message": f"Table '{table_name}' not found. Available: {list(Base.metadata.tables.keys())}",
            "data": None,
        }

    table = Base.metadata.tables[table_name]

    # Column info
    columns = []
    for col in table.columns:
        columns.append({
            "name": col.name,
            "type": str(col.type),
            "nullable": col.nullable,
            "primary_key": col.primary_key,
        })

    # Total count
    result = await db.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
    total = result.scalar()

    # Paginated data
    offset = (page - 1) * page_size
    result = await db.execute(
        text(f'SELECT * FROM "{table_name}" ORDER BY id DESC LIMIT :limit OFFSET :offset'),
        {"limit": page_size, "offset": offset},
    )
    rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]

    # Convert non-serializable types
    from datetime import datetime
    for row in rows:
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.isoformat()

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "table": table_name,
            "columns": columns,
            "total": total,
            "page": page,
            "page_size": page_size,
            "rows": rows,
        },
    }

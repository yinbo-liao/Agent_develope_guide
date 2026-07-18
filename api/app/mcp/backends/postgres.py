"""
Real Postgres MCP backend — replaces the fallback stubs with actual asyncpg queries.

Security: All queries are parameterized. No raw SQL string concatenation.
Destructive SQL patterns are blocked by the security firewall before execution.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.core.circuit_breaker import breaker_registry

logger = logging.getLogger(__name__)

# Destructive SQL patterns to block
_BLOCKED_PATTERNS = [
    "DROP", "TRUNCATE", "ALTER TABLE", "CREATE TABLE", "INSERT", "UPDATE", "DELETE"
]


class PostgresMCPBackend:
    """Real Postgres backend using asyncpg for MCP tool execution."""

    def __init__(self) -> None:
        self._pool = None
        self._initialized = False

    async def _ensure_pool(self):
        if self._initialized:
            return
        try:
            import asyncpg
            self._pool = await asyncpg.create_pool(
                settings.DATABASE_URL.replace("+asyncpg", ""),
                min_size=1,
                max_size=5,
            )
            self._initialized = True
            logger.info("Postgres MCP backend connected")
        except Exception as e:
            logger.warning("Postgres MCP backend unavailable: %s", e)
            self._initialized = True  # Don't retry

    async def query_database(self, sql: str, params: list[Any] | None = None) -> dict[str, Any]:
        """Execute a read-only parameterized query against the database."""
        # Security check — block destructive SQL
        upper_sql = sql.upper().strip()
        for pattern in _BLOCKED_PATTERNS:
            if upper_sql.startswith(pattern):
                return {"error": f"SQL pattern '{pattern}' is blocked by security policy. Only SELECT queries are permitted."}

        if not upper_sql.startswith("SELECT"):
            return {"error": "Only SELECT queries are permitted via MCP."}

        breaker = breaker_registry.get_mcp_breaker("postgres")

        try:
            async with breaker:
                await self._ensure_pool()
                if self._pool is None:
                    return {"error": "Postgres connection pool unavailable"}

                async with self._pool.acquire() as conn:
                    rows = await conn.fetch(sql, *(params or []))
                    columns = [k for k in rows[0].keys()] if rows else []
                    data = [dict(r) for r in rows]
                    return {"columns": columns, "rows": data, "row_count": len(data)}

        except RuntimeError:
            return {"error": "Circuit breaker open — Postgres MCP temporarily unavailable"}
        except Exception as e:
            logger.error("Postgres query failed: %s", e)
            return {"error": str(e)}

    async def describe_schema(self, table_name: str) -> dict[str, Any]:
        """Return column definitions for a table."""
        sql = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position
        """
        return await self.query_database(sql, [table_name])

    async def list_tables(self) -> dict[str, Any]:
        """Return all user tables in the public schema."""
        sql = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        return await self.query_database(sql)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._initialized = False


postgres_backend = PostgresMCPBackend()

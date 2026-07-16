from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import MCPToolCallAudit

logger = logging.getLogger(__name__)


class AuditLogInterceptor:
    def __init__(self) -> None:
        self._pending: dict[str, datetime] = {}

    async def on_request(
        self,
        session: AsyncSession,
        correlation_id: str,
        server_name: str,
        tool_name: str,
        args: dict[str, Any],
    ) -> None:
        self._pending[correlation_id] = datetime.now(timezone.utc)
        record = MCPToolCallAudit(
            correlation_id=correlation_id,
            server_name=server_name,
            tool_name=tool_name,
            arguments=json.dumps(self._sanitize_args(args)),
            result_summary="",
            status="pending",
            duration_ms=None,
        )
        session.add(record)
        await session.commit()

    async def on_response(
        self,
        session: AsyncSession,
        correlation_id: str,
        result: Any,
        status: str = "success",
    ) -> None:
        start_time = self._pending.pop(correlation_id, None)
        duration_ms = None
        if start_time:
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        summary = self._summarize_result(result)
        records = await session.execute(
            select(MCPToolCallAudit).where(MCPToolCallAudit.correlation_id == correlation_id)
        )
        rows = records.scalars().all()
        if rows:
            await session.execute(
                update(MCPToolCallAudit)
                .where(MCPToolCallAudit.correlation_id == correlation_id)
                .values(result_summary=summary, status=status, duration_ms=duration_ms)
            )
            await session.commit()

    def _sanitize_args(self, args: dict[str, Any]) -> dict[str, Any]:
        sensitive_keys = ("password", "token", "secret", "key", "credential", "auth")
        sanitized: dict[str, Any] = {}
        for key, value in args.items():
            sanitized[key] = "[REDACTED]" if any(
                marker in key.lower() for marker in sensitive_keys
            ) else value
        return sanitized

    def _summarize_result(self, result: Any) -> str:
        result_str = json.dumps(result, default=str) if not isinstance(result, str) else result
        return result_str[:500]


class RateLimitInterceptor:
    def __init__(self, max_calls_per_minute: int = 60) -> None:
        self.max_calls_per_minute = max_calls_per_minute
        self._calls: dict[str, list[datetime]] = {}

    def check(self, key: str) -> None:
        now = datetime.now(timezone.utc)
        minute_ago = now - timedelta(minutes=1)
        recent_calls = [timestamp for timestamp in self._calls.get(key, []) if timestamp > minute_ago]
        if len(recent_calls) >= self.max_calls_per_minute:
            raise RuntimeError(f"MCP rate limit exceeded for {key}")
        recent_calls.append(now)
        self._calls[key] = recent_calls

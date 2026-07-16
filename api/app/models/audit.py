from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MCPToolCallAudit(Base):
    __tablename__ = "mcp_tool_call_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    correlation_id: Mapped[str] = mapped_column(String(255), index=True)
    tool_name: Mapped[str] = mapped_column(String(255), index=True)
    server_name: Mapped[str] = mapped_column(String(255), index=True)
    arguments: Mapped[str] = mapped_column(Text())
    result_summary: Mapped[str] = mapped_column(Text(), default="")
    status: Mapped[str] = mapped_column(String(64), default="pending")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MCPServerHealth:
    name: str
    status: str
    enabled: bool
    tools: list[str]
    last_check: datetime
    message: str


class ResilientMCPClient:
    """Configuration-backed MCP manager with local fallback metadata."""

    def __init__(self) -> None:
        self._initialized = False
        self._server_health: dict[str, MCPServerHealth] = {}
        self._tool_catalog: dict[str, list[str]] = {}

    def _configured_servers(self) -> dict[str, dict[str, Any]]:
        return {
            "postgres": {
                "enabled": settings.MCP_POSTGRES_ENABLED,
                "tools": ["query_database_fallback", "describe_schema_fallback"],
                "message": "Fallback metadata available for database operations.",
            },
            "github": {
                "enabled": settings.MCP_GITHUB_ENABLED,
                "tools": ["list_pull_requests_fallback", "read_issue_fallback"],
                "message": "Fallback metadata available for GitHub operations.",
            },
            "puppeteer": {
                "enabled": settings.MCP_PUPPETEER_ENABLED,
                "tools": ["browser_snapshot_fallback", "browser_click_fallback"],
                "message": "Fallback metadata available for browser operations.",
            },
            "slack": {
                "enabled": settings.MCP_SLACK_ENABLED,
                "tools": ["post_message_fallback"],
                "message": "Fallback metadata available for Slack notifications.",
            },
        }

    async def initialize(self) -> None:
        if self._initialized:
            return
        now = datetime.now(timezone.utc)
        for server_name, server in self._configured_servers().items():
            enabled = bool(server["enabled"])
            status = "healthy" if enabled else "disabled"
            self._tool_catalog[server_name] = list(server["tools"])
            self._server_health[server_name] = MCPServerHealth(
                name=server_name,
                status=status,
                enabled=enabled,
                tools=list(server["tools"]),
                last_check=now,
                message=server["message"],
            )
        self._initialized = True
        logger.info("MCP manager initialized with %s servers", len(self._server_health))

    async def close(self) -> None:
        self._initialized = False

    async def get_tools(self) -> list[dict[str, Any]]:
        if not self._initialized:
            await self.initialize()
        tools: list[dict[str, Any]] = []
        for server_name, tool_names in self._tool_catalog.items():
            for tool_name in tool_names:
                tools.append({"server": server_name, "name": tool_name, "mode": "fallback"})
        return tools

    async def get_server_health(self) -> dict[str, MCPServerHealth]:
        if not self._initialized:
            await self.initialize()
        return self._server_health

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        health = self._server_health.get(server_name)
        if health is None or tool_name not in health.tools:
            raise RuntimeError(f"Unknown MCP tool {server_name}.{tool_name}")
        return {
            "server": server_name,
            "tool": tool_name,
            "mode": "fallback",
            "args": args,
            "result": f"Fallback execution placeholder for {server_name}.{tool_name}",
        }


mcp_tool_manager = ResilientMCPClient()

"""
Real GitHub MCP backend — replaces fallback stubs with actual GitHub API calls.

Requires GITHUB_TOKEN to be set in configuration.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.circuit_breaker import breaker_registry

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubMCPBackend:
    """Real GitHub backend using the GitHub REST API."""

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        return headers

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        breaker = breaker_registry.get_mcp_breaker("github")
        try:
            async with breaker:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    url = f"{GITHUB_API_BASE}{path}"
                    resp = await client.request(method, url, headers=self._headers(), **kwargs)
                    resp.raise_for_status()
                    return {"status": resp.status_code, "data": resp.json()}
        except RuntimeError:
            return {"error": "Circuit breaker open — GitHub MCP temporarily unavailable"}
        except httpx.HTTPStatusError as e:
            return {"error": f"GitHub API error: {e.response.status_code}", "detail": str(e)}
        except Exception as e:
            logger.error("GitHub MCP request failed: %s", e)
            return {"error": str(e)}

    async def list_pull_requests(self, repo: str, state: str = "open") -> dict[str, Any]:
        """List pull requests for a repository. Repo format: owner/repo."""
        return await self._request("GET", f"/repos/{repo}/pulls", params={"state": state, "per_page": 10})

    async def read_issue(self, repo: str, issue_number: int) -> dict[str, Any]:
        """Read a specific issue by number."""
        return await self._request("GET", f"/repos/{repo}/issues/{issue_number}")

    async def get_file(self, repo: str, path: str, ref: str = "main") -> dict[str, Any]:
        """Get file content from a repository."""
        return await self._request("GET", f"/repos/{repo}/contents/{path}", params={"ref": ref})


github_backend = GitHubMCPBackend()

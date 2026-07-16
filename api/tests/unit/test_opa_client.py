from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.security.opa_client import OPAPolicyClient


@pytest.mark.anyio
async def test_evaluate_returns_allowed_when_opa_says_yes() -> None:
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        allow_response = MagicMock()
        allow_response.json.return_value = {"result": True}
        allow_response.raise_for_status = MagicMock()

        violation_response = MagicMock()
        violation_response.json.return_value = {"result": []}
        violation_response.raise_for_status = MagicMock()

        mock_client.post = AsyncMock(side_effect=[allow_response, violation_response])

        client = OPAPolicyClient(opa_url="http://test-opa:8181")
        result = await client.evaluate(
            agent="frontend-dev", action="read", path="/frontend/src/App.tsx"
        )

    assert result["allowed"] is True
    assert result["violations"] == []


@pytest.mark.anyio
async def test_evaluate_fails_closed_on_http_error() -> None:
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        from httpx import HTTPError

        mock_client.post.side_effect = HTTPError("OPA unreachable")

        client = OPAPolicyClient(opa_url="http://test-opa:8181")
        result = await client.evaluate(
            agent="backend-dev", action="write", path="/api/app/models/workflow.py"
        )

    assert result["allowed"] is False
    assert len(result["violations"]) > 0


@pytest.mark.anyio
async def test_check_scope_delegates_to_evaluate() -> None:
    client = OPAPolicyClient(opa_url="http://test-opa:8181")
    client.evaluate = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "allowed": True,
            "violations": [],
            "input": {"agent": "governor", "action": "read", "path": "/"},
        }
    )

    allowed = await client.check_scope(
        agent="governor", action="read", path="/"
    )
    assert allowed is True


@pytest.mark.anyio
async def test_check_scope_returns_false_when_denied() -> None:
    client = OPAPolicyClient(opa_url="http://test-opa:8181")
    client.evaluate = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "allowed": False,
            "violations": [{"msg": "Agent cannot write to /api"}],
            "input": {"agent": "frontend-dev", "action": "write", "path": "/api/main.py"},
        }
    )

    allowed = await client.check_scope(
        agent="frontend-dev", action="write", path="/api/main.py"
    )
    assert allowed is False

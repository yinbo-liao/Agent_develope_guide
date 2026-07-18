from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_workflow_returns_202(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "test-user",
            "input_query": "Review the deployment plan for security impact.",
            "token_budget": 5000,
            "cost_budget_usd": 3.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 202
    data = response.json()
    # user_id is now taken from the JWT, not the request body
    assert data["user_id"] == "test-user-id"
    assert data["current_status"] == "pending"
    assert data["id"] != ""


@pytest.mark.anyio
async def test_create_workflow_rejects_empty_query(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "test-user",
            "input_query": "ab",  # below min_length=3
            "token_budget": 5000,
            "cost_budget_usd": 3.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_workflow_accepts_unauthenticated(async_client: AsyncClient) -> None:
    """In dev mode, unauthenticated requests should work (optional auth)."""
    response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "anonymous-user",
            "input_query": "Some valid query here.",
        },
    )
    assert response.status_code == 202


@pytest.mark.anyio
async def test_list_workflows(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await async_client.get("/api/v1/workflows", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.anyio
async def test_get_workflow_not_found(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await async_client.get(
        "/api/v1/workflows/nonexistent-id", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_and_get_workflow(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    create_response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "test-user",
            "input_query": "Test the workflow lifecycle end-to-end.",
            "token_budget": 10000,
            "cost_budget_usd": 5.0,
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 202
    workflow_id = create_response.json()["id"]

    get_response = await async_client.get(
        f"/api/v1/workflows/{workflow_id}", headers=auth_headers
    )
    assert get_response.status_code == 200
    detail = get_response.json()
    assert detail["id"] == workflow_id
    assert detail["input_query"] == "Test the workflow lifecycle end-to-end."
    # user_id comes from the token, not the request
    assert detail["user_id"] == "test-user-id"


@pytest.mark.anyio
async def test_cannot_access_other_users_workflow(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    viewer_auth_headers: dict[str, str],
) -> None:
    """A workflow created by one user should not be visible to another."""
    # Create workflow as admin
    create_response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "admin-user",
            "input_query": "This is an admin-only workflow.",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 202
    workflow_id = create_response.json()["id"]

    # Try to access as viewer
    get_response = await async_client.get(
        f"/api/v1/workflows/{workflow_id}", headers=viewer_auth_headers
    )
    assert get_response.status_code == 404  # Not found (not 403 — don't leak existence)

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_workflow_returns_202(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "test-user",
            "input_query": "Review the deployment plan for security impact.",
            "token_budget": 5000,
            "cost_budget_usd": 3.0,
        },
    )
    assert response.status_code == 202
    data = response.json()
    assert data["user_id"] == "test-user"
    assert data["current_status"] == "pending"
    assert data["id"] != ""


@pytest.mark.anyio
async def test_create_workflow_rejects_empty_query(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "test-user",
            "input_query": "ab",  # below min_length=3
            "token_budget": 5000,
            "cost_budget_usd": 3.0,
        },
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_list_workflows(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/workflows")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_get_workflow_not_found(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/workflows/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_and_get_workflow(async_client: AsyncClient) -> None:
    create_response = await async_client.post(
        "/api/v1/workflows",
        json={
            "user_id": "test-user",
            "input_query": "Test the workflow lifecycle end-to-end.",
            "token_budget": 10000,
            "cost_budget_usd": 5.0,
        },
    )
    assert create_response.status_code == 202
    workflow_id = create_response.json()["id"]

    get_response = await async_client.get(f"/api/v1/workflows/{workflow_id}")
    assert get_response.status_code == 200
    detail = get_response.json()
    assert detail["id"] == workflow_id
    assert detail["input_query"] == "Test the workflow lifecycle end-to-end."
    assert detail["user_id"] == "test-user"

from __future__ import annotations

import pytest

from app.services.model_router import MODEL_REGISTRY, ModelCapability, ModelRouter

router = ModelRouter()


def test_estimate_cost_for_known_model() -> None:
    cost = router.estimate_cost("claude-haiku-3-5", estimated_tokens=1000)
    assert cost > 0.0
    assert cost < 0.01


def test_estimate_cost_for_unknown_model() -> None:
    cost = router.estimate_cost("unknown-model", estimated_tokens=1000)
    assert cost == 0.0


@pytest.mark.anyio
async def test_select_model_returns_cheapest_for_fast_tasks() -> None:
    result = await router.select_model(
        user_id="starter-user", task_complexity="fast", estimated_tokens=1000
    )
    assert result["model"] in ("claude-haiku-3-5", "claude-sonnet-4-6")


@pytest.mark.anyio
async def test_select_model_for_complex_tasks() -> None:
    result = await router.select_model(
        user_id="professional-user", task_complexity="complex", estimated_tokens=5000
    )
    assert result["model"] in (
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "claude-haiku-3-5",
    )


@pytest.mark.anyio
async def test_select_model_for_free_tier() -> None:
    from app.services.cost_governor import BudgetTier, cost_governor

    cost_governor._user_tiers["free-user"] = BudgetTier.FREE
    result = await router.select_model(
        user_id="free-user", task_complexity="complex", estimated_tokens=1000
    )
    assert result["model"] == "claude-haiku-3-5"


def test_model_registry_has_expected_models() -> None:
    assert "claude-haiku-3-5" in MODEL_REGISTRY
    assert "claude-sonnet-4-6" in MODEL_REGISTRY
    assert "claude-opus-4-6" in MODEL_REGISTRY
    assert "gpt-4o" in MODEL_REGISTRY


def test_model_capabilities() -> None:
    haiku = MODEL_REGISTRY["claude-haiku-3-5"]
    assert ModelCapability.FAST in haiku["capabilities"]

    sonnet = MODEL_REGISTRY["claude-sonnet-4-6"]
    assert ModelCapability.BALANCED in sonnet["capabilities"]
    assert ModelCapability.VISION in sonnet["capabilities"]

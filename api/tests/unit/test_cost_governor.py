from __future__ import annotations

from app.services.cost_governor import BUDGET_CONFIGS, BudgetTier, CostGovernor


def test_get_budget_config_returns_default_tier() -> None:
    governor = CostGovernor()
    config = governor.get_budget_config("unknown-user")
    assert config.tier == BudgetTier.STARTER


def test_get_budget_config_for_known_tier() -> None:
    governor = CostGovernor()
    governor._user_tiers["enterprise-user"] = BudgetTier.ENTERPRISE
    config = governor.get_budget_config("enterprise-user")
    assert config.tier == BudgetTier.ENTERPRISE
    assert config.daily_token_limit == 10_000_000


def test_check_budget_allows_within_limits() -> None:
    governor = CostGovernor()
    governor._user_tiers["test-user"] = BudgetTier.STARTER
    allowed, details = governor.check_budget("test-user", estimated_tokens=100, estimated_cost=0.01)
    assert allowed is True
    assert details["tier"] == "starter"


def test_check_budget_rejects_over_token_limit() -> None:
    governor = CostGovernor()
    governor._user_tiers["test-user"] = BudgetTier.FREE
    allowed, details = governor.check_budget(
        "test-user", estimated_tokens=20_000, estimated_cost=0.0
    )
    assert allowed is False
    assert "token" in str(details.get("reason", "")).lower()


def test_check_budget_rejects_over_cost_limit() -> None:
    governor = CostGovernor()
    governor._user_tiers["test-user"] = BudgetTier.FREE
    allowed, details = governor.check_budget(
        "test-user", estimated_tokens=0, estimated_cost=5.0
    )
    assert allowed is False
    assert "cost" in str(details.get("reason", "")).lower()


def test_record_usage_updates_counters() -> None:
    governor = CostGovernor()
    governor._user_tiers["test-user"] = BudgetTier.STARTER
    governor.record_usage("test-user", "task-1", tokens=500, cost_usd=0.05, model="claude-haiku-3-5")

    usage = governor._current_usage("test-user")
    assert int(usage["tokens"]) == 500
    assert float(usage["cost"]) == 0.05


def test_get_status_returns_summary() -> None:
    governor = CostGovernor()
    governor._user_tiers["test-user"] = BudgetTier.PROFESSIONAL
    governor.record_usage("test-user", "task-1", tokens=1000, cost_usd=0.10, model="claude-sonnet-4-6")

    status = governor.get_status("test-user")
    assert status["user_id"] == "test-user"
    assert status["budget_tier"] == "professional"
    assert status["tokens_used"] == 1000
    assert status["current_cost_usd"] == 0.10


def test_budget_configs_all_tiers_defined() -> None:
    for tier in BudgetTier:
        assert tier in BUDGET_CONFIGS
        config = BUDGET_CONFIGS[tier]
        assert config.daily_token_limit > 0
        assert config.daily_cost_limit_usd > 0
        assert len(config.allowed_models) > 0

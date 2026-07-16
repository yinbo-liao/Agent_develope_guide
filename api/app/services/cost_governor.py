from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

from app.core.config import settings


class BudgetTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class BudgetConfig:
    tier: BudgetTier
    daily_token_limit: int
    daily_cost_limit_usd: float
    max_concurrent_workflows: int
    allowed_models: list[str]


BUDGET_CONFIGS = {
    BudgetTier.FREE: BudgetConfig(
        tier=BudgetTier.FREE,
        daily_token_limit=10_000,
        daily_cost_limit_usd=1.0,
        max_concurrent_workflows=1,
        allowed_models=["claude-haiku-3-5"],
    ),
    BudgetTier.STARTER: BudgetConfig(
        tier=BudgetTier.STARTER,
        daily_token_limit=100_000,
        daily_cost_limit_usd=10.0,
        max_concurrent_workflows=3,
        allowed_models=["claude-haiku-3-5", "claude-sonnet-4-6"],
    ),
    BudgetTier.PROFESSIONAL: BudgetConfig(
        tier=BudgetTier.PROFESSIONAL,
        daily_token_limit=1_000_000,
        daily_cost_limit_usd=100.0,
        max_concurrent_workflows=10,
        allowed_models=["claude-haiku-3-5", "claude-sonnet-4-6", "claude-opus-4-6"],
    ),
    BudgetTier.ENTERPRISE: BudgetConfig(
        tier=BudgetTier.ENTERPRISE,
        daily_token_limit=10_000_000,
        daily_cost_limit_usd=1000.0,
        max_concurrent_workflows=50,
        allowed_models=["claude-haiku-3-5", "claude-sonnet-4-6", "claude-opus-4-6", "gpt-4o"],
    ),
}


class CostGovernor:
    """In-memory cost governance for Wave 4 with the same public shape as a future Redis-backed service."""

    def __init__(self) -> None:
        self._user_tiers: dict[str, BudgetTier] = {}
        self._usage: dict[tuple[str, str], dict[str, float | int | dict[str, int] | list[dict[str, str | float]]]] = {}

    def get_budget_config(self, user_id: str) -> BudgetConfig:
        tier = self._user_tiers.get(user_id, BudgetTier.STARTER)
        return BUDGET_CONFIGS[tier]

    def _usage_key(self, user_id: str) -> tuple[str, str]:
        return user_id, datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _current_usage(self, user_id: str) -> dict[str, object]:
        key = self._usage_key(user_id)
        if key not in self._usage:
            self._usage[key] = {
                "tokens": 0,
                "cost": 0.0,
                "models": {},
                "alerts": [],
                "updated_at": datetime.now(timezone.utc),
            }
        return self._usage[key]

    def check_budget(
        self,
        user_id: str,
        estimated_tokens: int = 0,
        estimated_cost: float = 0.0,
    ) -> tuple[bool, dict[str, object]]:
        config = self.get_budget_config(user_id)
        usage = self._current_usage(user_id)
        current_tokens = int(usage["tokens"])
        current_cost = float(usage["cost"])

        details = {
            "tier": config.tier.value,
            "daily_token_limit": config.daily_token_limit,
            "daily_cost_limit_usd": config.daily_cost_limit_usd,
            "current_tokens": current_tokens,
            "current_cost_usd": round(current_cost, 6),
            "projected_tokens": current_tokens + estimated_tokens,
            "projected_cost_usd": round(current_cost + estimated_cost, 6),
        }

        if current_tokens + estimated_tokens > config.daily_token_limit:
            details["reason"] = "Daily token limit exceeded"
            return False, details
        if current_cost + estimated_cost > config.daily_cost_limit_usd:
            details["reason"] = "Daily cost limit exceeded"
            return False, details
        return True, details

    def record_usage(
        self,
        user_id: str,
        task_id: str,
        tokens: int,
        cost_usd: float,
        model: str,
    ) -> None:
        del task_id
        usage = self._current_usage(user_id)
        usage["tokens"] = int(usage["tokens"]) + tokens
        usage["cost"] = round(float(usage["cost"]) + cost_usd, 6)
        models = usage["models"]
        assert isinstance(models, dict)
        models[model] = int(models.get(model, 0)) + tokens
        usage["updated_at"] = datetime.now(timezone.utc)
        self._record_alerts(user_id)

    def _record_alerts(self, user_id: str) -> None:
        config = self.get_budget_config(user_id)
        usage = self._current_usage(user_id)
        alerts = usage["alerts"]
        assert isinstance(alerts, list)
        current_cost = float(usage["cost"])
        usage_percent = 0.0 if config.daily_cost_limit_usd == 0 else current_cost / config.daily_cost_limit_usd
        thresholds = [0.5, 0.8, 1.0]
        sent_thresholds = {float(alert["threshold"]) for alert in alerts}
        for threshold in thresholds:
            if usage_percent >= threshold and threshold not in sent_thresholds:
                alerts.append(
                    {
                        "threshold": threshold * 100,
                        "triggered_at": datetime.now(timezone.utc).isoformat(),
                    }
                )

    def get_status(self, user_id: str) -> dict[str, object]:
        config = self.get_budget_config(user_id)
        usage = self._current_usage(user_id)
        current_cost = float(usage["cost"])
        current_tokens = int(usage["tokens"])
        model_breakdown = usage["models"]
        alerts = usage["alerts"]
        assert isinstance(model_breakdown, dict)
        assert isinstance(alerts, list)
        return {
            "user_id": user_id,
            "current_cost_usd": round(current_cost, 6),
            "daily_limit_usd": config.daily_cost_limit_usd,
            "usage_percent": round((current_cost / config.daily_cost_limit_usd) * 100, 2)
            if config.daily_cost_limit_usd
            else 0.0,
            "tokens_used": current_tokens,
            "model_breakdown": [
                {"model": model, "tokens": tokens}
                for model, tokens in sorted(model_breakdown.items(), key=lambda item: item[1], reverse=True)
            ],
            "alerts": alerts,
            "budget_tier": config.tier.value,
            "window_start": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat(),
        }


cost_governor = CostGovernor()

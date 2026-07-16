from __future__ import annotations

from enum import Enum
from typing import Any

from app.services.cost_governor import cost_governor


class ModelCapability(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"
    VISION = "vision"


MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "claude-haiku-3-5": {
        "capabilities": [ModelCapability.FAST],
        "cost_per_1k_prompt": 0.00025,
        "cost_per_1k_completion": 0.00125,
    },
    "claude-sonnet-4-6": {
        "capabilities": [ModelCapability.BALANCED, ModelCapability.VISION],
        "cost_per_1k_prompt": 0.003,
        "cost_per_1k_completion": 0.015,
    },
    "claude-opus-4-6": {
        "capabilities": [ModelCapability.POWERFUL, ModelCapability.VISION],
        "cost_per_1k_prompt": 0.015,
        "cost_per_1k_completion": 0.075,
    },
    "gpt-4o": {
        "capabilities": [ModelCapability.BALANCED, ModelCapability.VISION],
        "cost_per_1k_prompt": 0.005,
        "cost_per_1k_completion": 0.015,
    },
}


class ModelRouter:
    def estimate_cost(self, model_name: str, estimated_tokens: int) -> float:
        model = MODEL_REGISTRY.get(model_name)
        if model is None:
            return 0.0
        prompt_tokens = int(estimated_tokens * 0.7)
        completion_tokens = estimated_tokens - prompt_tokens
        return round(
            (prompt_tokens / 1000) * model["cost_per_1k_prompt"]
            + (completion_tokens / 1000) * model["cost_per_1k_completion"],
            6,
        )

    async def select_model(
        self,
        user_id: str,
        task_complexity: str = "medium",
        estimated_tokens: int = 1000,
    ) -> dict[str, Any]:
        budget = cost_governor.get_budget_config(user_id)
        candidates = list(budget.allowed_models)
        preference_order = {
            "fast": ["claude-haiku-3-5", "claude-sonnet-4-6", "gpt-4o", "claude-opus-4-6"],
            "medium": ["claude-sonnet-4-6", "gpt-4o", "claude-haiku-3-5", "claude-opus-4-6"],
            "complex": ["claude-opus-4-6", "claude-sonnet-4-6", "gpt-4o", "claude-haiku-3-5"],
        }
        ordered_candidates = [
            model for model in preference_order.get(task_complexity, preference_order["medium"]) if model in candidates
        ]
        for model_name in ordered_candidates:
            estimated_cost = self.estimate_cost(model_name, estimated_tokens)
            allowed, details = await cost_governor.check_budget(user_id, estimated_tokens, estimated_cost)
            if allowed:
                return {
                    "model": model_name,
                    "estimated_cost": estimated_cost,
                    "budget_status": details,
                    "reason": f"Selected for {task_complexity} workload",
                }
        fallback = ordered_candidates[0] if ordered_candidates else candidates[0]
        return {
            "model": fallback,
            "estimated_cost": self.estimate_cost(fallback, estimated_tokens),
            "budget_status": {"reason": "Fallback model selected"},
            "reason": "Budget-constrained fallback",
        }


model_router = ModelRouter()

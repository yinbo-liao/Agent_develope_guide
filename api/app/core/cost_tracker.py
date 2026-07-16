from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UsageRecord:
    tokens: int
    cost_usd: float
    model: str


class CostTracker:
    """Small helper for estimating and recording usage in Wave 2."""

    def estimate(self, text: str, model: str = "wave2-simulated") -> UsageRecord:
        tokens = max(1, len(text.split())) * 8
        cost = round(tokens * 0.000002, 6)
        return UsageRecord(tokens=tokens, cost_usd=cost, model=model)


cost_tracker = CostTracker()

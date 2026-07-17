from __future__ import annotations

from fastapi import APIRouter, Depends, status

from fastapi import APIRouter, Depends, Query, status

from app.core.cache import cached
from app.core.deps import get_current_user, get_optional_user
from app.services.cost_governor import cost_governor
from app.services.semantic_cache import get_stats as get_cache_stats

router = APIRouter(prefix="/cost", tags=["Cost"])


@router.get("/status", status_code=status.HTTP_200_OK)
@cached("cost_status", ttl=30)
async def cost_status(
    user_id: str = Query(default="demo-user"),
    current_user: dict[str, object] | None = Depends(get_optional_user),
) -> dict[str, object]:
    effective_user = str(current_user["user_id"]) if current_user else user_id
    return await cost_governor.get_status(effective_user)


@router.get("/optimization-insights", status_code=status.HTTP_200_OK)
async def optimization_insights(
    user_id: str = Query(default="demo-user"),
    current_user: dict[str, object] | None = Depends(get_optional_user),
) -> dict[str, object]:
    """Return cost optimization metrics: cache savings, cascade savings, etc."""
    effective_user = str(current_user["user_id"]) if current_user else user_id
    cache_stats = get_cache_stats()
    status = await cost_governor.get_status(effective_user)

    cache_hits = cache_stats["hits"]
    estimated_cache_savings = round(cache_hits * 0.005, 4)

    return {
        "user_id": effective_user,
        "semantic_cache": {
            "hits": cache_stats["hits"],
            "misses": cache_stats["misses"],
            "total_queries": cache_stats["total"],
            "hit_rate": round(
                cache_stats["hits"] / max(1, cache_stats["total"]) * 100, 1
            ),
            "estimated_savings_usd": estimated_cache_savings,
        },
        "cascade_routing": {
            "enabled": True,
            "description": "Tiered execution: cheapest model first, escalate only if needed",
        },
        "prompt_compression": {
            "enabled": True,
            "max_context_items": 3,
            "max_snippet_chars": 200,
        },
        "projected_monthly_savings_usd": round(estimated_cache_savings * 30, 2),
        "current_usage": status,
    }

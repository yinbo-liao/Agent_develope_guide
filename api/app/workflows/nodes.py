from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.circuit_breaker import breaker_registry
from app.core.metrics import track_llm_cost
from app.models.workflow import WorkflowRun
from app.services.cost_governor import cost_governor
from app.services.llm_client import LLMClient
from app.services.model_router import model_router
from app.services.semantic_cache import check_cache, record_hit, record_miss, store_cache
from app.services.vector_store import retrieve_context
from app.workflows.state import RiskLevel, WorkflowStatus


async def validate_input(run: WorkflowRun) -> dict[str, Any]:
    query = run.input_query.strip()
    if not query:
        return {
            "current_step": "validate_input",
            "current_status": WorkflowStatus.FAILED.value,
            "risk_level": RiskLevel.CRITICAL.value,
            "error_info": "Query cannot be empty.",
        }
    return {
        "current_step": "validate_input",
        "current_status": WorkflowStatus.RETRIEVING.value,
        "updated_at": datetime.now(timezone.utc),
    }


async def retrieve_context_node(run: WorkflowRun) -> dict[str, Any]:
    results = await retrieve_context(run.input_query, top_k=5)
    return {
        "current_step": "retrieve_context",
        "current_status": WorkflowStatus.ASSESSING.value,
        "retrieval_results": results,
        "updated_at": datetime.now(timezone.utc),
    }


async def assess_risk(run: WorkflowRun) -> dict[str, Any]:
    query = run.input_query.lower()
    score = 0
    factors: list[str] = []

    critical_patterns = {
        r"\b(payment|credit.?card|ssn|social.security)\b": "Sensitive financial or personal data",
        r"\b(drop|truncate|destroy)\b": "Destructive operation requested",
        r"\b(sudo|root|superuser)\b": "Privilege escalation language",
    }
    high_patterns = {
        r"\b(delete|remove)\b": "Deletion request",
        r"\b(update|modify|alter)\b": "Modification request",
        r"\b(secret|token|password|key)\b": "Credential-related access",
    }

    for pattern, reason in critical_patterns.items():
        if re.search(pattern, query):
            score += 50
            factors.append(f"CRITICAL: {reason}")

    for pattern, reason in high_patterns.items():
        if re.search(pattern, query):
            score += 20
            factors.append(f"HIGH: {reason}")

    if run.retrieval_results:
        score += min(10, len(run.retrieval_results) * 2)

    if score >= 50:
        level = RiskLevel.CRITICAL
    elif score >= 30:
        level = RiskLevel.HIGH
    elif score >= 10:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    return {
        "current_step": "assess_risk",
        "current_status": WorkflowStatus.EXECUTING.value
        if level is RiskLevel.LOW
        else WorkflowStatus.REVIEWING.value
        if level is RiskLevel.CRITICAL
        else WorkflowStatus.EXECUTING.value,
        "risk_level": level.value,
        "risk_factors": factors,
        "updated_at": datetime.now(timezone.utc),
    }


async def auto_generate_response(run: WorkflowRun) -> dict[str, Any]:
    model_choice = await model_router.select_model(
        user_id=run.user_id,
        task_complexity="fast",
        estimated_tokens=max(256, run.token_budget - run.total_tokens_used),
    )
    allowed, budget_status = await cost_governor.check_budget(
        run.user_id,
        estimated_tokens=max(256, run.token_budget - run.total_tokens_used),
        estimated_cost=float(model_choice["estimated_cost"]),
    )
    if not allowed:
        return {
            "current_step": "budget_guard",
            "current_status": WorkflowStatus.FAILED.value,
            "error_info": str(budget_status.get("reason", "Budget check failed")),
            "updated_at": datetime.now(timezone.utc),
        }

    model_name = str(model_choice["model"])

    # Check semantic cache before generating
    cached_response = await check_cache(run.input_query, model_name)
    if cached_response is not None:
        record_hit()
        await cost_governor.record_usage(
            user_id=run.user_id,
            task_id=run.id,
            tokens=cached_response.get("tokens_used", 0),
            cost_usd=0.0,
            model=model_name,
        )
        return {
            "current_step": "auto_generate_response",
            "current_status": WorkflowStatus.COMPLETED.value,
            "final_response": cached_response.get("content", ""),
            "agent_finding": f"Cached response served (model={model_name}).",
            "total_tokens_used": run.total_tokens_used + cached_response.get("tokens_used", 0),
            "cost_usd": round(run.cost_usd, 6),
            "completed_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    record_miss()

    breaker = breaker_registry.get_llm_breaker(model_name)
    async with breaker:
        response = await LLMClient.generate(
            prompt=run.input_query,
            context=run.retrieval_results or [],
            max_tokens=max(256, run.token_budget - run.total_tokens_used),
            temperature=0.2,
            model=model_name,
        )

    await cost_governor.record_usage(
        user_id=run.user_id,
        task_id=run.id,
        tokens=response["tokens_used"],
        cost_usd=response["cost_usd"],
        model=response["model"],
    )
    track_llm_cost(str(response["model"]), float(response["cost_usd"]))

    # Store in semantic cache for future reuse
    await store_cache(run.input_query, model_name, response)

    return {
        "current_step": "auto_generate_response",
        "current_status": WorkflowStatus.COMPLETED.value,
        "final_response": response["content"],
        "agent_finding": f"Direct response generated in low-risk path with {response['model']}.",
        "total_tokens_used": run.total_tokens_used + response["tokens_used"],
        "cost_usd": round(run.cost_usd + response["cost_usd"], 6),
        "completed_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


async def complex_analysis(run: WorkflowRun) -> dict[str, Any]:
    complexity = "complex" if run.risk_level == RiskLevel.HIGH.value else "medium"
    model_choice = await model_router.select_model(
        user_id=run.user_id,
        task_complexity=complexity,
        estimated_tokens=max(512, run.token_budget - run.total_tokens_used),
    )
    allowed, budget_status = await cost_governor.check_budget(
        run.user_id,
        estimated_tokens=max(512, run.token_budget - run.total_tokens_used),
        estimated_cost=float(model_choice["estimated_cost"]),
    )
    if not allowed:
        return {
            "current_step": "budget_guard",
            "current_status": WorkflowStatus.FAILED.value,
            "error_info": str(budget_status.get("reason", "Budget check failed")),
            "updated_at": datetime.now(timezone.utc),
        }

    model_name = str(model_choice["model"])
    breaker = breaker_registry.get_llm_breaker(model_name)
    async with breaker:
        response = await LLMClient.generate(
            prompt=f"Provide a more careful operational analysis for: {run.input_query}",
            context=run.retrieval_results or [],
            max_tokens=max(512, run.token_budget - run.total_tokens_used),
            temperature=0.1,
            model=model_name,
        )
    await cost_governor.record_usage(
        user_id=run.user_id,
        task_id=run.id,
        tokens=response["tokens_used"],
        cost_usd=response["cost_usd"],
        model=response["model"],
    )
    track_llm_cost(str(response["model"]), float(response["cost_usd"]))
    return {
        "current_step": "complex_analysis",
        "current_status": WorkflowStatus.COMPLETED.value,
        "final_response": response["content"],
        "agent_finding": f"Escalated analysis path completed with {response['model']}.",
        "total_tokens_used": run.total_tokens_used + response["tokens_used"],
        "cost_usd": round(run.cost_usd + response["cost_usd"], 6),
        "completed_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


async def human_review_node(run: WorkflowRun) -> dict[str, Any]:
    if run.human_decision == "approved":
        return {
            "current_step": "human_review_approved",
            "current_status": WorkflowStatus.COMPLETED.value,
            "is_human_review_needed": False,
            "final_response": (
                "Human review approved the task. Execution can continue in later waves "
                "with tool orchestration and live transport."
            ),
            "agent_finding": "Human reviewer approved the workflow.",
            "completed_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

    if run.human_decision == "rejected":
        return {
            "current_step": "human_review_rejected",
            "current_status": WorkflowStatus.CANCELLED.value,
            "is_human_review_needed": False,
            "error_info": "Human review rejected the request.",
            "completed_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

    return {
        "current_step": "human_review_pending",
        "current_status": WorkflowStatus.REVIEWING.value,
        "is_human_review_needed": True,
        "review_deadline": datetime.now(timezone.utc) + timedelta(minutes=30),
        "updated_at": datetime.now(timezone.utc),
    }

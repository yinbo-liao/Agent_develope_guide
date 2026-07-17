from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.websocket_manager import ws_manager
from app.models.human_review import HumanReviewDecision
from app.models.workflow import WorkflowRun
from app.workflows.nodes import adjust_risk_bias, human_review_node


def _adjust_factor_bias(factor: str, outcome: str) -> None:
    """Map a risk factor description back to its regex pattern and adjust bias."""
    # Map known factor descriptions to their regex patterns
    factor_to_pattern = {
        "CRITICAL: Sensitive financial or personal data": r"\b(payment|credit.?card|ssn|social.security)\b",
        "CRITICAL: Destructive operation requested": r"\b(drop|truncate|destroy)\b",
        "CRITICAL: Privilege escalation language": r"\b(sudo|root|superuser)\b",
        "HIGH: Deletion request": r"\b(delete|remove)\b",
        "HIGH: Modification request": r"\b(update|modify|alter)\b",
        "HIGH: Credential-related access": r"\b(secret|token|password|key)\b",
    }
    pattern = factor_to_pattern.get(factor)
    if pattern:
        adjust_risk_bias(pattern, outcome)


async def process_human_decision(
    session: AsyncSession,
    task_id: str,
    reviewer_id: str,
    decision: str,
    comment: str = "",
) -> WorkflowRun:
    result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == task_id))
    run = result.scalar_one()

    run.human_decision = decision
    run.human_comment = comment
    run.updated_at = datetime.now(timezone.utc)

    # Adaptive risk: adjust pattern biases based on reviewer decision
    if run.risk_level in ("critical", "high") and decision == "approved":
        for factor in run.risk_factors:
            _adjust_factor_bias(factor, "approved")
    elif run.risk_level in ("low", "medium") and decision == "rejected":
        for factor in run.risk_factors:
            _adjust_factor_bias(factor, "rejected")

    session.add(
        HumanReviewDecision(
            workflow_id=task_id,
            reviewer_id=reviewer_id,
            decision=decision,
            comment=comment,
        )
    )

    updates = await human_review_node(run)
    for key, value in updates.items():
        setattr(run, key, value)

    await session.commit()
    await session.refresh(run)
    await ws_manager.broadcast(
        task_id,
        {
            "type": "human_review",
            "status": run.current_status,
            "currentStep": run.current_step,
            "decision": run.human_decision,
            "comment": run.human_comment,
            "isHumanReviewNeeded": run.is_human_review_needed,
            "finalResponse": run.final_response,
            "error": run.error_info,
        },
    )
    return run

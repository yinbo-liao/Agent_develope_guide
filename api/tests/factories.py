from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.models.human_review import HumanReviewDecision
from app.models.workflow import WorkflowRun
from app.workflows.state import RiskLevel, WorkflowStatus


def make_workflow_run(
    *,
    id: str | None = None,
    user_id: str = "test-user",
    session_id: str | None = None,
    input_query: str = "Test workflow query",
    current_step: str = "created",
    current_status: str = WorkflowStatus.PENDING.value,
    risk_level: str = RiskLevel.LOW.value,
    risk_factors: list[str] | None = None,
    retrieval_results: list[dict[str, object]] | None = None,
    agent_finding: str | None = None,
    final_response: str | None = None,
    error_info: str | None = None,
    retry_count: int = 0,
    max_retries: int = 3,
    total_tokens_used: int = 0,
    token_budget: int = 10000,
    cost_usd: float = 0.0,
    cost_budget_usd: float = 5.0,
    is_human_review_needed: bool = False,
    human_decision: str | None = None,
    human_comment: str | None = None,
    review_deadline: datetime | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> WorkflowRun:
    """Factory for creating WorkflowRun instances for tests."""
    return WorkflowRun(
        id=id or str(uuid.uuid4()),
        user_id=user_id,
        session_id=session_id,
        input_query=input_query,
        current_step=current_step,
        current_status=current_status,
        risk_level=risk_level,
        risk_factors=risk_factors or [],
        retrieval_results=retrieval_results,
        agent_finding=agent_finding,
        final_response=final_response,
        error_info=error_info,
        retry_count=retry_count,
        max_retries=max_retries,
        total_tokens_used=total_tokens_used,
        token_budget=token_budget,
        cost_usd=cost_usd,
        cost_budget_usd=cost_budget_usd,
        is_human_review_needed=is_human_review_needed,
        human_decision=human_decision,
        human_comment=human_comment,
        review_deadline=review_deadline,
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=updated_at or datetime.now(timezone.utc),
        completed_at=completed_at,
    )


def make_human_review_decision(
    *,
    id: int | None = None,
    workflow_id: str = "test-workflow-id",
    reviewer_id: str = "reviewer-1",
    decision: str = "approved",
    comment: str = "",
    created_at: datetime | None = None,
) -> HumanReviewDecision:
    """Factory for creating HumanReviewDecision instances for tests."""
    return HumanReviewDecision(
        id=id,  # type: ignore[arg-type]
        workflow_id=workflow_id,
        reviewer_id=reviewer_id,
        decision=decision,
        comment=comment,
        created_at=created_at or datetime.now(timezone.utc),
    )

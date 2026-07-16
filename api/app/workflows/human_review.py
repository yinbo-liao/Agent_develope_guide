from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.websocket_manager import ws_manager
from app.models.human_review import HumanReviewDecision
from app.models.workflow import WorkflowRun
from app.workflows.nodes import human_review_node


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

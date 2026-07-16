from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.core.websocket_manager import ws_manager
from app.models.workflow import WorkflowRun
from app.workflows.graph import workflow_graph
from app.workflows.state import WorkflowStatus

logger = logging.getLogger(__name__)


def apply_updates(run: WorkflowRun, updates: dict[str, object]) -> None:
    for key, value in updates.items():
        setattr(run, key, value)
    if "updated_at" not in updates:
        run.updated_at = datetime.now(timezone.utc)


async def broadcast_workflow_snapshot(
    run: WorkflowRun,
    event_type: str,
    extra: dict[str, object] | None = None,
) -> None:
    await ws_manager.broadcast(
        run.id,
        {
            "type": event_type,
            "status": run.current_status,
            "currentStep": run.current_step,
            "riskLevel": run.risk_level,
            "isHumanReviewNeeded": run.is_human_review_needed,
            "finalResponse": run.final_response,
            "error": run.error_info,
            "totalTokens": run.total_tokens_used,
            "totalCost": run.cost_usd,
            **(extra or {}),
        },
    )


async def execute_workflow(session: AsyncSession, task_id: str) -> WorkflowRun:
    result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == task_id))
    run = result.scalar_one()

    run.current_status = WorkflowStatus.VALIDATING.value
    run.current_step = "queued"
    run.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(run)
    await broadcast_workflow_snapshot(run, "workflow_start", {"message": "Workflow queued"})

    try:
        steps = await workflow_graph.execute(run)
        for step in steps:
            apply_updates(run, step)
            await broadcast_workflow_snapshot(
                run,
                "step",
                {
                    "stepName": run.current_step,
                    "stepStatus": run.current_status,
                    "reviewData": {
                        "factors": run.risk_factors,
                        "deadline": run.review_deadline.isoformat() if run.review_deadline else None,
                    },
                },
            )
        await session.commit()
        await session.refresh(run)
        await broadcast_workflow_snapshot(run, "workflow_complete")
        return run
    except Exception as exc:
        logger.exception("Workflow execution failed for %s", task_id)
        run.current_status = WorkflowStatus.FAILED.value
        run.current_step = "workflow_error"
        run.error_info = str(exc)
        run.retry_count += 1
        run.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(run)
        await broadcast_workflow_snapshot(run, "error")
        return run


async def run_workflow_in_new_session(task_id: str) -> None:
    async with SessionLocal() as session:
        await execute_workflow(session, task_id)

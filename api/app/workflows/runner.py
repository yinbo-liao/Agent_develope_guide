from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.core.dead_letter import push as dlq_push
from app.core.websocket_manager import ws_manager
from app.models.workflow import WorkflowRun
from app.workflows.graph import workflow_graph
from app.workflows.state import WorkflowStatus

logger = logging.getLogger(__name__)

# Concurrency gate: limit simultaneous workflow executions
# Default: 10 concurrent workflows, overridable per tier
_workflow_semaphore = asyncio.Semaphore(10)

# Exceptions that should trigger a retry (transient errors)
RETRYABLE_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    asyncio.TimeoutError,
    OSError,
)

# Exceptions that should NOT be retried (permanent errors)
FATAL_EXCEPTIONS = (
    ValueError,
    TypeError,
    KeyError,
    AttributeError,
)


def _remediation_for(exc: Exception) -> str | None:
    """Return a remediation strategy string for known error types, or None."""
    msg = str(exc).lower()
    if "timeout" in msg or isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
        return "timeout"
    if "circuit" in msg and "open" in msg:
        return "circuit_open"
    if "budget" in msg or "limit exceeded" in msg or "cost limit" in msg:
        return "budget"
    if "connection" in msg or "refused" in msg:
        return "connection"
    return None


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
    async with _workflow_semaphore:
        return await _execute_workflow_inner(session, task_id)


async def _execute_workflow_inner(session: AsyncSession, task_id: str) -> WorkflowRun:
    result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == task_id))
    run = result.scalar_one()

    run.current_status = WorkflowStatus.VALIDATING.value
    run.current_step = "queued"
    run.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(run)
    await broadcast_workflow_snapshot(run, "workflow_start", {"message": "Workflow queued"})

    while run.retry_count <= run.max_retries:
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
                            "deadline": (
                                run.review_deadline.isoformat()
                                if run.review_deadline
                                else None
                            ),
                        },
                    },
                )
            await session.commit()
            await session.refresh(run)
            await broadcast_workflow_snapshot(run, "workflow_complete")
            return run

        except FATAL_EXCEPTIONS as exc:
            logger.exception("Fatal workflow error for %s", task_id)
            run.current_status = WorkflowStatus.FAILED.value
            run.current_step = "workflow_error"
            run.error_info = str(exc)
            run.retry_count += 1
            run.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(run)
            dlq_push(run)
            await broadcast_workflow_snapshot(run, "error")
            return run

        except Exception as exc:
            remediation = _remediation_for(exc)
            run.retry_count += 1
            logger.warning(
                "Workflow %s attempt %d/%d failed [%s]: %s",
                task_id, run.retry_count, run.max_retries + 1,
                remediation or "unknown", exc,
            )

            # Auto-remediation adjustments
            if remediation == "circuit_open":
                # Queue and retry when circuit closes
                run.error_info = "Circuit breaker open — queued for retry when circuit closes."
            elif remediation == "budget":
                run.error_info = "Budget exceeded — workflow deferred."
                # No retry on budget — push to DLQ immediately
                run.current_status = WorkflowStatus.FAILED.value
                run.updated_at = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(run)
                dlq_push(run)
                await broadcast_workflow_snapshot(run, "error")
                return run

            if run.retry_count > run.max_retries:
                logger.error("Workflow %s exhausted all retries", task_id)
                run.current_status = WorkflowStatus.FAILED.value
                run.current_step = "workflow_error"
                run.error_info = (
                    f"Exhausted {run.max_retries} retries. "
                    f"Last error [{remediation}]: {exc}"
                )
                run.updated_at = datetime.now(timezone.utc)
                await session.commit()
                await session.refresh(run)
                dlq_push(run)
                await broadcast_workflow_snapshot(run, "error")
                return run

            # Exponential backoff with remediation-specific adjustments
            delay = min(2 ** run.retry_count, 60)
            if remediation == "timeout":
                delay = min(2 ** run.retry_count, 120)  # longer wait for timeouts
            logger.info("Retrying workflow %s in %ds (remediation: %s)...", task_id, delay, remediation)
            run.error_info = f"Retry {run.retry_count}/{run.max_retries} [{remediation}]: {exc}"
            run.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await broadcast_workflow_snapshot(run, "step", {"stepName": "retry", "stepStatus": f"retrying_{remediation}"})
            await asyncio.sleep(delay)


async def run_workflow_in_new_session(task_id: str) -> None:
    async with SessionLocal() as session:
        await execute_workflow(session, task_id)

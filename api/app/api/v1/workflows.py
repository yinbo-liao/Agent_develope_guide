from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dead_letter import (
    get as dlq_get,
    list_entries as dlq_list,
    mark_replayed as dlq_mark_replayed,
    serialize_entry as dlq_serialize,
)
from app.core.deps import get_current_user, get_optional_user
from app.core.websocket_manager import ws_manager
from app.models.workflow import WorkflowRun
from app.workflows.runner import run_workflow_in_new_session
from app.workflows.state import WorkflowCreateRequest, WorkflowDetail, WorkflowSummary

router = APIRouter(prefix="/workflows", tags=["Workflows"])


def to_summary(run: WorkflowRun) -> WorkflowSummary:
    return WorkflowSummary.model_validate(run, from_attributes=True)


def to_detail(run: WorkflowRun) -> WorkflowDetail:
    return WorkflowDetail.model_validate(run, from_attributes=True)


@router.post("", response_model=WorkflowSummary, status_code=status.HTTP_202_ACCEPTED)
async def create_workflow(
    payload: WorkflowCreateRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict[str, object] = Depends(get_current_user),
) -> WorkflowSummary:
    workflow = WorkflowRun(
        id=str(uuid.uuid4()),
        user_id=str(current_user["user_id"]),
        session_id=payload.session_id,
        input_query=payload.input_query,
        token_budget=payload.token_budget,
        cost_budget_usd=payload.cost_budget_usd,
    )
    session.add(workflow)
    await session.commit()
    await session.refresh(workflow)

    await ws_manager.broadcast(
        workflow.id,
        {
            "type": "workflow_created",
            "status": workflow.current_status,
            "currentStep": workflow.current_step,
            "isHumanReviewNeeded": workflow.is_human_review_needed,
        },
    )

    background_tasks.add_task(run_workflow_in_new_session, workflow.id)
    return to_summary(workflow)


@router.get("", response_model=list[WorkflowSummary])
async def list_workflows(
    session: AsyncSession = Depends(get_db_session),
    current_user: dict[str, object] = Depends(get_current_user),
) -> list[WorkflowSummary]:
    stmt = select(WorkflowRun).where(
        WorkflowRun.user_id == str(current_user["user_id"])
    ).order_by(WorkflowRun.created_at.desc())

    result = await session.execute(stmt)
    runs = result.scalars().all()
    return [to_summary(run) for run in runs]


@router.get("/{task_id}", response_model=WorkflowDetail)
async def get_workflow(
    task_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict[str, object] = Depends(get_current_user),
) -> WorkflowDetail:
    result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == task_id))
    run = result.scalar_one_or_none()
    if run is None or run.user_id != str(current_user["user_id"]):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return to_detail(run)


# ---------------------------------------------------------------------------
# Dead Letter Queue
# ---------------------------------------------------------------------------

@router.get("/dlq/entries", response_model=list[dict[str, object]])
async def list_dlq_entries(
    current_user: dict[str, object] = Depends(get_current_user),
) -> list[dict[str, object]]:
    """List dead-letter-queued workflows for the authenticated user."""
    return dlq_list(user_id=str(current_user["user_id"]))


@router.post("/dlq/{dlq_id}/replay", status_code=status.HTTP_202_ACCEPTED)
async def replay_dlq_entry(
    dlq_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict[str, object] = Depends(get_current_user),
) -> dict[str, object]:
    """Replay a dead-lettered workflow as a new workflow run."""
    entry = dlq_get(dlq_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="DLQ entry not found")
    if entry.get("user_id") != str(current_user["user_id"]):
        raise HTTPException(status_code=404, detail="DLQ entry not found")

    payload = dlq_serialize(entry)
    workflow = WorkflowRun(
        id=str(uuid.uuid4()),
        user_id=payload["user_id"],
        input_query=payload["input_query"],
        token_budget=payload["token_budget"],
        cost_budget_usd=payload["cost_budget_usd"],
    )
    session.add(workflow)
    await session.commit()
    await session.refresh(workflow)
    dlq_mark_replayed(dlq_id)
    background_tasks.add_task(run_workflow_in_new_session, workflow.id)
    return {"status": "replayed", "new_task_id": workflow.id}

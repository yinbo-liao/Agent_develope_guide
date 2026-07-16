from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.workflow import WorkflowRun
from app.workflows.human_review import process_human_decision
from app.workflows.state import WorkflowDecisionRequest, WorkflowDetail

router = APIRouter(prefix="/human-review", tags=["Human Review"])


@router.post("/decide", response_model=WorkflowDetail, status_code=status.HTTP_200_OK)
async def decide_workflow(
    payload: WorkflowDecisionRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict[str, object] = Depends(get_current_user),
) -> WorkflowDetail:
    result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == payload.task_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    updated = await process_human_decision(
        session=session,
        task_id=payload.task_id,
        reviewer_id=payload.reviewer_id,
        decision=payload.decision,
        comment=payload.comment,
    )
    return WorkflowDetail.model_validate(updated, from_attributes=True)

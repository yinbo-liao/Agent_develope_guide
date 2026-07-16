from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.sse_manager import sse_manager
from app.core.websocket_manager import ws_manager
from app.models.workflow import WorkflowRun
from app.workflows.human_review import process_human_decision

router = APIRouter(prefix="/events", tags=["Events"])


async def build_state_payload(task_id: str) -> dict[str, object]:
    async with SessionLocal() as session:
        result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == task_id))
        run = result.scalar_one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return {
            "type": "state",
            "taskId": run.id,
            "status": run.current_status,
            "currentStep": run.current_step,
            "riskLevel": run.risk_level,
            "isHumanReviewNeeded": run.is_human_review_needed,
            "finalResponse": run.final_response,
            "error": run.error_info,
            "totalTokens": run.total_tokens_used,
            "totalCost": run.cost_usd,
            "reviewData": {
                "decision": run.human_decision,
                "comment": run.human_comment,
                "deadline": run.review_deadline.isoformat() if run.review_deadline else None,
                "factors": run.risk_factors,
            },
        }


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str) -> None:
    await ws_manager.add_connection(task_id, websocket)
    try:
        await websocket.send_json(await build_state_payload(task_id))
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            if message_type == "ping":
                await websocket.send_json({"type": "pong", "taskId": task_id})
            elif message_type == "status":
                await websocket.send_json(await build_state_payload(task_id))
            elif message_type == "resume":
                async with SessionLocal() as session:
                    run = await process_human_decision(
                        session=session,
                        task_id=task_id,
                        reviewer_id=str(data.get("reviewerId", "anonymous")),
                        decision=str(data.get("decision", "approved")),
                        comment=str(data.get("comment", "")),
                    )
                await ws_manager.broadcast(
                    task_id,
                    {
                        "type": "human_review",
                        "status": run.current_status,
                        "decision": run.human_decision,
                        "comment": run.human_comment,
                        "isHumanReviewNeeded": run.is_human_review_needed,
                        "currentStep": run.current_step,
                    },
                )
                await websocket.send_json(await build_state_payload(task_id))
    except WebSocketDisconnect:
        ws_manager.remove_connection(task_id, websocket)


@router.get("/sse/{task_id}")
async def sse_endpoint(request: Request, task_id: str) -> StreamingResponse:
    del request
    return StreamingResponse(
        sse_manager.subscribe(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/state/{task_id}")
async def state_endpoint(task_id: str) -> dict[str, object]:
    return await build_state_payload(task_id)

from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.services.cost_governor import cost_governor

router = APIRouter(prefix="/cost", tags=["Cost"])


@router.get("/status", status_code=status.HTTP_200_OK)
async def cost_status(user_id: str = Query(..., min_length=1)) -> dict[str, object]:
    return cost_governor.get_status(user_id)

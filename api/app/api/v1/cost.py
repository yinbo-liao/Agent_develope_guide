from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.deps import get_current_user
from app.services.cost_governor import cost_governor

router = APIRouter(prefix="/cost", tags=["Cost"])


@router.get("/status", status_code=status.HTTP_200_OK)
async def cost_status(
    current_user: dict[str, object] = Depends(get_current_user),
) -> dict[str, object]:
    return await cost_governor.get_status(str(current_user["user_id"]))

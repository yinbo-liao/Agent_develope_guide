from __future__ import annotations

from datetime import datetime, timezone

import redis.asyncio as redis
from fastapi import APIRouter, status

from app.core.config import settings
from app.core.database import check_database_health

router = APIRouter()


async def check_redis_health() -> bool:
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await client.ping()
        return True
    except Exception:
        return False
    finally:
        await client.aclose()


@router.get("", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> dict[str, object]:
    database_ok = await check_database_health()
    redis_ok = await check_redis_health()
    ready = database_ok and redis_ok

    return {
        "status": "ready" if ready else "degraded",
        "checks": {"database": database_ok, "redis": redis_ok},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

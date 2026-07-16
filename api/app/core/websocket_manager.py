from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import redis.asyncio as redis
from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisWebSocketManager:
    """Local websocket fanout with optional Redis pub/sub bridging."""

    def __init__(self, redis_url: str = settings.REDIS_URL) -> None:
        self.redis_url = redis_url
        self.redis_client: redis.Redis | None = None
        self.pubsub: redis.client.PubSub | None = None
        self.local_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._listener_task: asyncio.Task[None] | None = None
        self._initialized = False

    async def connect(self) -> None:
        if self._initialized:
            return

        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.psubscribe("task:*")
            self._listener_task = asyncio.create_task(self._redis_listener())
            logger.info("WebSocket manager connected with Redis pub/sub")
        except Exception:
            logger.warning("Redis pub/sub unavailable; WebSocket manager using local-only mode")
            self.redis_client = None
            self.pubsub = None
            self._listener_task = None
        finally:
            self._initialized = True

    async def disconnect(self) -> None:
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.punsubscribe()
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()

        for task_id, websockets in list(self.local_connections.items()):
            for websocket in list(websockets):
                try:
                    await websocket.close(code=1001)
                except Exception:
                    pass
            self.local_connections.pop(task_id, None)
        self._initialized = False

    async def _redis_listener(self) -> None:
        assert self.pubsub is not None
        async for message in self.pubsub.listen():
            if message.get("type") != "pmessage":
                continue
            channel = str(message.get("channel", ""))
            task_id = channel.split(":")[-1]
            raw_data = message.get("data")
            if not isinstance(raw_data, str):
                continue
            try:
                payload = json.loads(raw_data)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid Redis websocket payload")
                continue
            await self._forward_to_local(task_id, payload)

    async def add_connection(self, task_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.local_connections[task_id].add(websocket)
        await websocket.send_json(
            {
                "type": "connection",
                "status": "connected",
                "taskId": task_id,
                "transport": "websocket",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def remove_connection(self, task_id: str, websocket: WebSocket) -> None:
        if task_id not in self.local_connections:
            return
        self.local_connections[task_id].discard(websocket)
        if not self.local_connections[task_id]:
            self.local_connections.pop(task_id, None)

    async def _forward_to_local(self, task_id: str, message: dict[str, object]) -> None:
        stale_connections: list[WebSocket] = []
        for websocket in self.local_connections.get(task_id, set()):
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)
                else:
                    stale_connections.append(websocket)
            except Exception:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.remove_connection(task_id, websocket)

    async def broadcast(self, task_id: str, message: dict[str, object]) -> None:
        enriched = {
            "taskId": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **message,
        }
        if self.redis_client:
            try:
                await self.redis_client.publish(f"task:{task_id}", json.dumps(enriched))
                return
            except Exception:
                logger.warning("Redis publish failed; falling back to local broadcast")
        await self._forward_to_local(task_id, enriched)

    async def event_stream(self, task_id: str) -> AsyncGenerator[dict[str, object], None]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue()

        class QueueSocket:
            client_state = WebSocketState.CONNECTED

            async def send_json(self, payload: dict[str, object]) -> None:
                await queue.put(payload)

        bridge = QueueSocket()
        self.local_connections[task_id].add(bridge)  # type: ignore[arg-type]
        await queue.put(
            {
                "type": "connection",
                "status": "connected",
                "taskId": task_id,
                "transport": "sse",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        try:
            while True:
                payload = await queue.get()
                yield payload
        finally:
            self.local_connections[task_id].discard(bridge)  # type: ignore[arg-type]
            if not self.local_connections[task_id]:
                self.local_connections.pop(task_id, None)


ws_manager = RedisWebSocketManager()

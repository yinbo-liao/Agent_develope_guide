from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from app.core.websocket_manager import ws_manager


class SSEManager:
    async def subscribe(self, task_id: str) -> AsyncGenerator[str, None]:
        async for payload in ws_manager.event_stream(task_id):
            yield self._format_sse(payload)

    def _format_sse(self, data: dict[str, object]) -> str:
        return f"data: {json.dumps(data)}\n\n"


sse_manager = SSEManager()

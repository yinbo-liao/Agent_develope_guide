from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass
class CircuitBreakerState:
    failure_count: int = 0
    opened_at: datetime | None = None


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = CircuitBreakerState()

    def _is_open(self) -> bool:
        if self._state.opened_at is None:
            return False
        return datetime.now(timezone.utc) < self._state.opened_at + timedelta(
            seconds=self.recovery_timeout
        )

    async def __aenter__(self) -> "CircuitBreaker":
        if self._is_open():
            raise RuntimeError("Circuit breaker is open")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        _: Any,
    ) -> bool:
        if exc is None:
            self._state.failure_count = 0
            self._state.opened_at = None
            return False

        self._state.failure_count += 1
        if self._state.failure_count >= self.failure_threshold:
            self._state.opened_at = datetime.now(timezone.utc)
        return False

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerState:
    failure_count: int = 0
    opened_at: datetime | None = None
    state: BreakerState = BreakerState.CLOSED
    on_state_change: Callable[[BreakerState, BreakerState], None] | None = None


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "default",
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self._state = CircuitBreakerState()
        self._half_open_probe: bool = False

    def _transition_to(self, new_state: BreakerState) -> None:
        old = self._state.state
        if old != new_state:
            self._state.state = new_state
            logger.info(
                "CircuitBreaker[%s]: %s -> %s", self.name, old.value, new_state.value
            )
            if self._state.on_state_change:
                self._state.on_state_change(old, new_state)

    def _is_open(self) -> bool:
        if self._state.opened_at is None:
            return False
        elapsed = datetime.now(timezone.utc) - self._state.opened_at
        if elapsed >= timedelta(seconds=self.recovery_timeout):
            # Transition to half-open — allow one probe request
            self._transition_to(BreakerState.HALF_OPEN)
            return False
        return True

    async def __aenter__(self) -> "CircuitBreaker":
        if self._state.state == BreakerState.OPEN and self._is_open():
            raise RuntimeError(f"CircuitBreaker[{self.name}] is open")
        # HALF_OPEN: allow exactly one probe through
        if self._state.state == BreakerState.HALF_OPEN:
            self._half_open_probe = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        _: Any,
    ) -> bool:
        if exc is None:
            # Success — reset the breaker
            self._state.failure_count = 0
            self._state.opened_at = None
            self._half_open_probe = False
            self._transition_to(BreakerState.CLOSED)
            return False

        self._state.failure_count += 1
        if self._state.failure_count >= self.failure_threshold:
            self._state.opened_at = datetime.now(timezone.utc)
            self._transition_to(BreakerState.OPEN)
        return False


class CircuitBreakerRegistry:
    """Registry of named circuit breaker instances for different backends."""

    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}

    def get(self, name: str) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name=name)
        return self._breakers[name]

    def get_llm_breaker(self, model: str) -> CircuitBreaker:
        return self.get(f"llm:{model}")

    def get_mcp_breaker(self, server: str) -> CircuitBreaker:
        return self.get(f"mcp:{server}")


breaker_registry = CircuitBreakerRegistry()

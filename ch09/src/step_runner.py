"""Chapter 9 — step runner for production graphs.

Bounded retry with injected jitter/clock, idempotency keys so a duplicated
delivery does not double a side effect, and a circuit breaker that opens
after K failures and then fails fast.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, TypeVar

T = TypeVar("T")

SleepFn = Callable[[float], None]
RngFn = Callable[[], float]  # in [0, 1)
ClockFn = Callable[[], float]


class CircuitOpenError(RuntimeError):
    """The breaker is open; the function is not called."""


@dataclass
class StepRunner:
    max_attempts: int = 3
    breaker_threshold: int = 5
    base_delay: float = 0.05
    sleep: SleepFn = field(default=lambda _seconds: None)
    rng: RngFn = field(default=lambda: 0.0)
    clock: ClockFn = field(default=lambda: 0.0)

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.breaker_threshold < 1:
            raise ValueError("breaker_threshold must be >= 1")
        self._failures: int = 0
        self._open: bool = False
        self._cache: dict[str, object] = {}
        self._seen_keys: set[str] = set()
        self.delays: list[float] = []
        self.calls_prevented: int = 0

    @property
    def is_open(self) -> bool:
        return self._open

    @property
    def failure_count(self) -> int:
        return self._failures

    def _jittered_delay(self, attempt_index: int) -> float:
        # attempt_index is 0-based for the retry *after* a failure.
        raw = self.base_delay * (2 ** attempt_index)
        jitter = self.rng()  # 0..1
        delay = raw * (0.5 + jitter)  # in [0.5, 1.5) * backoff
        return delay

    def run(self, fn: Callable[[], T], *, idempotency_key: str | None = None) -> T:
        if self._open:
            self.calls_prevented += 1
            raise CircuitOpenError(
                f"circuit open after {self._failures} failures; failing fast"
            )

        if idempotency_key is not None and idempotency_key in self._cache:
            return self._cache[idempotency_key]  # type: ignore[return-value]

        last_exc: BaseException | None = None
        for attempt in range(self.max_attempts):
            try:
                result = fn()
            except Exception as exc:
                last_exc = exc
                self._failures += 1
                if self._failures >= self.breaker_threshold:
                    self._open = True
                if attempt + 1 >= self.max_attempts or self._open:
                    break
                delay = self._jittered_delay(attempt)
                self.delays.append(delay)
                self.sleep(delay)
                continue
            # success: reset consecutive? Spec: "after K failures breaker is open".
            # A success clears the failure streak so a later flaky call can retry.
            self._failures = 0
            if idempotency_key is not None:
                self._cache[idempotency_key] = result
            return result

        assert last_exc is not None
        raise last_exc

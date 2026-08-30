from __future__ import annotations

import pytest

from step_runner import CircuitOpenError, StepRunner


def test_flaky_function_succeeds_within_retries() -> None:
    sleeps: list[float] = []
    rng_values = iter([0.0, 0.5, 1.0])

    def rng() -> float:
        return next(rng_values, 0.0)

    runner = StepRunner(
        max_attempts=3,
        breaker_threshold=10,
        base_delay=0.1,
        sleep=lambda s: sleeps.append(s),
        rng=rng,
    )
    box = {"n": 0}

    def flaky() -> str:
        box["n"] += 1
        if box["n"] < 3:
            raise RuntimeError(f"fail {box['n']}")
        return "ok"

    assert runner.run(flaky) == "ok"
    assert box["n"] == 3
    assert len(sleeps) == 2
    # Jitter is applied: delay = base * 2^attempt * (0.5 + rng)
    assert sleeps[0] == pytest.approx(0.1 * (0.5 + 0.0))
    assert sleeps[1] == pytest.approx(0.2 * (0.5 + 0.5))


def test_duplicate_idempotency_key_applies_side_effect_once() -> None:
    runner = StepRunner(max_attempts=1, breaker_threshold=10, sleep=lambda _s: None)
    box = {"n": 0}

    def effect() -> int:
        box["n"] += 1
        return box["n"]

    a = runner.run(effect, idempotency_key="refund-17")
    b = runner.run(effect, idempotency_key="refund-17")
    c = runner.run(effect, idempotency_key="refund-18")
    assert a == 1
    assert b == 1
    assert c == 2
    assert box["n"] == 2


def test_breaker_opens_after_k_failures_and_fails_fast() -> None:
    K = 3
    runner = StepRunner(max_attempts=1, breaker_threshold=K, sleep=lambda _s: None)
    box = {"n": 0}

    def always_fail() -> None:
        box["n"] += 1
        raise RuntimeError("down")

    for _ in range(K):
        with pytest.raises(RuntimeError):
            runner.run(always_fail)
    assert box["n"] == K
    assert runner.is_open is True

    with pytest.raises(CircuitOpenError):
        runner.run(always_fail)
    # Fail fast: the function is not called again.
    assert box["n"] == K
    assert runner.calls_prevented == 1


def test_success_resets_failure_streak() -> None:
    runner = StepRunner(max_attempts=1, breaker_threshold=3, sleep=lambda _s: None)
    box = {"n": 0}

    def sometimes() -> str:
        box["n"] += 1
        if box["n"] in (1, 2, 4):
            raise RuntimeError("x")
        return "ok"

    with pytest.raises(RuntimeError):
        runner.run(sometimes)
    with pytest.raises(RuntimeError):
        runner.run(sometimes)
    assert runner.run(sometimes) == "ok"
    assert runner.is_open is False
    with pytest.raises(RuntimeError):
        runner.run(sometimes)
    assert runner.is_open is False  # only one failure since reset

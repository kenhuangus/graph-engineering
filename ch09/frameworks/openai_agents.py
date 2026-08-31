"""Chapter 09 — Operating Graphs in Production — OpenAI Agents SDK port.

Step runner: retry + jitter, idempotency, circuit breaker.

Runner retries are not idempotency. Wrap the side effect in StepRunner.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch09" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from step_runner import CircuitOpenError, StepRunner
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch09_agent",
        instructions="Step runner: retry + jitter, idempotency, circuit breaker.",
        tools=[run],
        handoffs=[],
    )


def run():
    box = {"n": 0}

    def flaky():
        box["n"] += 1
        if box["n"] < 3:
            raise RuntimeError("transient")
        return "ok"

    runner = StepRunner(max_attempts=3, breaker_threshold=5, base_delay=0, sleep=lambda _d: None, rng=lambda: 0.0)
    first = runner.run(flaky, idempotency_key="refund-1")
    second = runner.run(flaky, idempotency_key="refund-1")
    return {"first": first, "second": second, "calls": box["n"]}


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(invoke())

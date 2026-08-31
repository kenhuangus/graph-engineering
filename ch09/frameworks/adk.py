"""Chapter 09 — Operating Graphs in Production — Google ADK 2.0 port.

Step runner: retry + jitter, idempotency, circuit breaker.

RetryConfig on the node. A Workflow does not replace idempotency keys.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch09" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from step_runner import CircuitOpenError, StepRunner
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch09_worker",
        model="stub",
        instruction="Step runner: retry + jitter, idempotency, circuit breaker.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch09_adk", sub_agents=[worker], description="RetryConfig on the node. A Workflow does not replace idempotency keys.")


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


if __name__ == "__main__":
    print(build().run(None))

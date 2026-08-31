"""Chapter 09 — Operating Graphs in Production — CrewAI port.

Step runner: retry + jitter, idempotency, circuit breaker.

kickoff() twice is not at-least-once. Put StepRunner under the task body.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch09" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from step_runner import CircuitOpenError, StepRunner
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch09 engineer",
        goal="Step runner: retry + jitter, idempotency, circuit breaker.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Step runner: retry + jitter, idempotency, circuit breaker.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


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


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(invoke())

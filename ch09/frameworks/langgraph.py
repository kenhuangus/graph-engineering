"""Chapter 09 — Operating Graphs in Production — LangGraph port.

Step runner: retry + jitter, idempotency, circuit breaker.

Topology: step
Compiled StateGraph. Nodes are functions; the SDK owns the edges.

Live: `pip install langgraph` then swap the fallback StateGraph for
`from langgraph.graph import StateGraph, START, END`.
No API key is required for this deterministic port.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch09" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from step_runner import CircuitOpenError, StepRunner
from runtime import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("step", lambda s, _n="step": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge(START, "step")
    g.add_edge("step", END)
    return g.compile()


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
    print(run())

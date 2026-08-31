"""Chapter 13 — Testing, Evaluation, and Verification — OpenAI Agents SDK port.

check_trace: halt, join, unconstrained spend.

Do not ask an Agent whether the join completed. check_trace reads the walk.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch13" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from trace_invariants import JoinSpec, TraceSpec, check_trace
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch13_agent",
        instructions="check_trace: halt, join, unconstrained spend.",
        tools=[run],
        handoffs=[],
    )


def run():
    spec = TraceSpec(
        halt="halt",
        joins=(JoinSpec("research", ("web", "docs"), "write"),),
        gate_nodes=("human",),
        spend_nodes=("apply",),
    )
    good = check_trace(["web", "docs", "write", "human", "apply", "halt"], spec)
    bad = check_trace(["write", "apply", "halt"], spec)
    return {"good": [v.code for v in good], "bad": [v.code for v in bad]}


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(run())

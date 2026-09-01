"""Chapter 13 — Testing, Evaluation, and Verification of Agent Graphs — OpenAI Agents SDK port.

check_trace: halt, join, unconstrained spend.

Do not ask an Agent whether the join completed. check_trace reads the walk.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This file imports agents.Agent / Runner. A local Model subclass drives the tool loop; no OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch13" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from trace_invariants import JoinSpec, TraceSpec, check_trace
from agents import Agent, Runner, handoff
from runtime import homework_openai_agent, run_openai


def build():
    _ = (Agent, Runner, handoff)
    return homework_openai_agent(
        name="ch13_agent",
        instructions="check_trace: halt, join, unconstrained spend.",
        fn=run,
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
    return run_openai(build(), payload)


if __name__ == "__main__":
    print(invoke())

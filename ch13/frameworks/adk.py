"""Chapter 13 — Testing, Evaluation, and Verification — Google ADK 2.0 port.

check_trace: halt, join, unconstrained spend.

Eval is a node after the run, or a CI job. It does not call a model.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch13" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from trace_invariants import JoinSpec, TraceSpec, check_trace
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch13_worker",
        model="stub",
        instruction="check_trace: halt, join, unconstrained spend.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch13_adk", sub_agents=[worker], description="Eval is a node after the run, or a CI job. It does not call a model.")


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


if __name__ == "__main__":
    print(build().run(None))

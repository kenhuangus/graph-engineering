"""Chapter 10 — The Computer Science Behind Graph Engineering — Google ADK 2.0 port.

Kahn topological sort, cycle detection, ready-set on a diamond.

A diamond is Sequential + Parallel wrappers, or a Workflow with a join. A back-edge is not a DAG.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch10" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from kahn import has_cycle, ready_set, topological_sort
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch10_worker",
        model="stub",
        instruction="Kahn topological sort, cycle detection, ready-set on a diamond.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch10_adk", sub_agents=[worker], description="A diamond is Sequential + Parallel wrappers, or a Workflow with a join. A back-edge is not a DAG.")


def run():
    nodes = ["A", "B", "C", "D"]
    diamond = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
    cycle = [("A", "B"), ("B", "C"), ("C", "A")]
    return {
        "order": topological_sort(nodes, diamond),
        "ready": sorted(ready_set(nodes, diamond, done={"A", "B"})),
        "cycle": has_cycle(["A", "B", "C"], cycle),
    }


if __name__ == "__main__":
    print(build().run(None))

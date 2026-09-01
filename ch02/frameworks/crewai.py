"""Chapter 02 — Execution Graphs and Memory Graphs — CrewAI port.

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

One agent, one task. A crew of three 'G_A / G_K / trace' voters is a costume.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This file imports crewai.Agent / Task / Crew / Process. A BaseLLM subclass drives kickoff() offline; no provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch02" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_kinds import GraphObject, classify
from crewai import Agent, Crew, Process, Task
from runtime import homework_crew, run_crew


def build():
    _ = (Agent, Task, Process)
    return homework_crew(
        role="ch02 engineer",
        goal="Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.",
        description="Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.",
        fn=run,
    )


def run(obj=None):
    if obj is None:
        obj = GraphObject(
            name="refund-graph",
            node_kinds=("agent", "tool", "human"),
            edge_kinds=("unconditional", "conditional"),
            nodes_do_work=True,
            edges_are_facts=False,
            persists_beyond_run=False,
            is_one_run_recording=False,
            nodes_run=True,
        )
    return classify(obj)


def invoke(inputs=None):
    return run_crew(build(), inputs)


if __name__ == "__main__":
    print(invoke())

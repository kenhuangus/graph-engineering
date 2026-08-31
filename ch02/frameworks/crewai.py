"""Chapter 02 — Two Graphs, One Word — CrewAI port.

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

One agent, one task. A crew of three 'G_A / G_K / trace' voters is a costume.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch02" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_kinds import GraphObject, classify
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch02 engineer",
        goal="Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


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
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(invoke())

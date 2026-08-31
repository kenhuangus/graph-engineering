"""Chapter 10 — The Computer Science Behind Graph Engineering — CrewAI port.

Kahn topological sort, cycle detection, ready-set on a diamond.

Process.sequential cannot fire B and C together. Admit the join or do not draw a diamond.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch10" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from kahn import has_cycle, ready_set, topological_sort
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch10 engineer",
        goal="Kahn topological sort, cycle detection, ready-set on a diamond.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Kahn topological sort, cycle detection, ready-set on a diamond.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run():
    nodes = ["A", "B", "C", "D"]
    diamond = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
    cycle = [("A", "B"), ("B", "C"), ("C", "A")]
    return {
        "order": topological_sort(nodes, diamond),
        "ready": sorted(ready_set(nodes, diamond, done={"A", "B"})),
        "cycle": has_cycle(["A", "B", "C"], cycle),
    }


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(run())

"""Chapter 10 — The Computer Science Behind Graph Engineering — CrewAI port.

Kahn topological sort, cycle detection, ready-set on a diamond.

Process.sequential cannot fire B and C together. Admit the join or do not draw a diamond.

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
sys.path.insert(0, str(_ROOT / "ch10" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from kahn import has_cycle, ready_set, topological_sort
from crewai import Agent, Crew, Process, Task
from runtime import homework_crew, run_crew


def build():
    _ = (Agent, Task, Process)
    return homework_crew(
        role="ch10 engineer",
        goal="Kahn topological sort, cycle detection, ready-set on a diamond.",
        description="Kahn topological sort, cycle detection, ready-set on a diamond.",
        fn=run,
    )


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
    return run_crew(build(), inputs)


if __name__ == "__main__":
    print(invoke())

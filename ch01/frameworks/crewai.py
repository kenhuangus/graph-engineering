"""Chapter 01 — Graph Engineering Is Topology You Own — CrewAI port.

Reconstruct a directed naming graph from speech-act events.

Sequential crew: ingest events, then assemble the graph. A hierarchical manager would invent edges.

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
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from crewai import Agent, Crew, Process, Task
from runtime import homework_crew, run_crew


def build():
    _ = (Agent, Task, Process)
    return homework_crew(
        role="ch01 engineer",
        goal="Reconstruct a directed naming graph from speech-act events.",
        description="Reconstruct a directed naming graph from speech-act events.",
        fn=run,
    )


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


def invoke(inputs=None):
    return run_crew(build(), inputs)


if __name__ == "__main__":
    print(invoke())

"""Chapter 01 — The Week the Word Arrived — CrewAI port.

Reconstruct a directed naming graph from speech-act events.

Sequential crew: ingest events, then assemble the graph. A hierarchical manager would invent edges.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch01 engineer",
        goal="Reconstruct a directed naming graph from speech-act events.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Reconstruct a directed naming graph from speech-act events.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(invoke())

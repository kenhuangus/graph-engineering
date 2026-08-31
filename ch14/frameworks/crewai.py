"""Chapter 14 — After the Word Dies — CrewAI port.

retirement_report: dead nodes, dead edges, candidates.

No crew. Inventory is a graph query.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch14" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from retirement import GraphDecl, retirement_report
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch14 engineer",
        goal="retirement_report: dead nodes, dead edges, candidates.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="retirement_report: dead nodes, dead edges, candidates.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run():
    spec = GraphDecl(
        nodes=("classify", "research", "specialist", "write", "halt"),
        edges=(
            ("classify", "research"),
            ("research", "write"),
            ("classify", "specialist"),
            ("specialist", "write"),
            ("write", "halt"),
        ),
        halt="halt",
    )
    traces = [
        ["classify", "research", "write", "halt"],
        ["classify", "research", "write", "halt"],
    ]
    return retirement_report(spec, traces)


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(run())

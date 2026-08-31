"""Chapter 05 — When Not to Build a Graph — CrewAI port.

Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.

Do not staff a three-agent sequential crew for one paragraph. One agent, one task, or no crew.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch05" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from napkin import JobSpec, napkin_test
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch05 engineer",
        goal="Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run(job=None):
    if job is None:
        job = JobSpec(workers=1, tools=("status_page",), fanout=False)
    return napkin_test(job)


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(run())

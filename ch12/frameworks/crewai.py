"""Chapter 12 — Graph Intelligence — CrewAI port.

One-layer message passing. This is G_L, not an agent graph.

A crew of nodes is the category error this chapter exists to prevent.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch12" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from message_passing import message_pass, normalize
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch12 engineer",
        goal="One-layer message passing. This is G_L, not an agent graph.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="One-layer message passing. This is G_L, not an agent graph.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run():
    embeddings = {"a": [1.0, 0.0], "b": [0.0, 1.0], "c": [1.0, 0.0]}
    edges = [("a", "b")]
    out = message_pass(embeddings, edges, directed=False)
    isolated = normalize(embeddings["c"])
    return {"a": out["a"], "c": out["c"], "isolated": isolated, "moved": out["a"] != isolated}


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(run())

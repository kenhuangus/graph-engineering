"""Chapter 04 — Anatomy of an Agent Graph — CrewAI port.

Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.

A kickoff that does not call the crew if validate_spec raises.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch04" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_spec import Edge, GraphSpec, Node, StateSchema, validate_spec
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch04 engineer",
        goal="Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run(spec=None):
    if spec is None:
        spec = GraphSpec(
            nodes=(
                Node("scout", "agent"),
                Node("worker", "agent"),
                Node("review", "evaluator"),
                Node("human", "human"),
                Node("halt", "tool"),
            ),
            edges=(
                Edge("scout", "worker", "unconditional"),
                Edge("worker", "review", "unconditional"),
                Edge("review", "scout", "conditional", guard="verdict == fail AND n < 3"),
                Edge("review", "human", "conditional", guard="verdict == pass"),
                Edge("human", "halt", "unconditional"),
            ),
            state=StateSchema(fields={"draft": "str", "notes": "list"}, reducers={"notes": "append"}),
            halt_node="halt",
            human_interrupt="human",
        )
    return validate_spec(spec)


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(invoke())

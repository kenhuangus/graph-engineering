"""Chapter 03 — Harness as Paradigm — Siblings, Not a Ladder — CrewAI port.

Score a structured system against prompt / context / loop / graph / memory.

One agent, one task. Do not staff five role-agents and vote.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch03" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from five_layers import SystemDescription, score_layers
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch03 engineer",
        goal="Score a structured system against prompt / context / loop / graph / memory.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Score a structured system against prompt / context / loop / graph / memory.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run(desc=None):
    if desc is None:
        desc = SystemDescription(
            has_system_prompt=True,
            single_turn=False,
            window_curation=False,
            retrieved_chunks_in_window=0,
            observe_act_verify=True,
            inner_loop_retries=2,
            tool_calls_inside_one_worker=True,
            named_nodes=(),
            named_edges=(),
            fan_out=False,
            join=False,
            halt_node=False,
            persistent_store=False,
            triple_retrieval=False,
            provenance_on_facts=False,
            entity_types=(),
        )
    return score_layers(desc)


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(invoke())

"""Chapter 11 — Security, Identity, and Governance — CrewAI port.

Default-deny invoke, bound resume, cut-vertex reachability.

Do not put spend on a worker the manager can invent. Pre-assign, or do not crew it.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch11" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from authz_graph import AuthzGraph, Principal
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch11 engineer",
        goal="Default-deny invoke, bound resume, cut-vertex reachability.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Default-deny invoke, bound resume, cut-vertex reachability.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run():
    g = AuthzGraph(
        nodes=("start", "gate", "spend", "halt", "public"),
        edges=(("start", "gate"), ("gate", "spend"), ("spend", "halt"), ("start", "public"), ("public", "halt")),
        principals=(Principal("ken", "human"), Principal("stranger", "human")),
    )
    g.allow_invoke("ken", "spend")
    g.bind_resume("ken", "t1", "hash-a")
    return {
        "ken": g.can_invoke("ken", "spend"),
        "stranger": g.can_invoke("stranger", "spend"),
        "bad_resume": g.may_resume("ken", "t1", "hash-b"),
        "cut": g.is_cut_vertex("start", "spend", "gate"),
    }


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(invoke())

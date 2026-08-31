"""Chapter 08 — Knowledge Graphs as Memory — CrewAI port.

Ingest typed triples, query, walk neighbors, refuse execute().

One researcher-with-a-store is a costume. One tool-bearing agent, or no crew.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch08" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from triple_store import TripleStore
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch08 engineer",
        goal="Ingest typed triples, query, walk neighbors, refuse execute().",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Ingest typed triples, query, walk neighbors, refuse execute().",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run(records=None):
    store = TripleStore()
    rows = records or [
        {"s": "redis", "p": "superseded_by", "o": "nats", "provenance": "adr-142"},
        {"s": "nats", "p": "used_by", "o": "payments-api", "provenance": "runbook"},
    ]
    store.ingest(rows)
    try:
        store.execute()
        execute = "called"
    except TypeError:
        execute = "refused"
    return {"count": len(store), "neighbors": sorted(store.neighbors("redis", depth=2)), "execute": execute}


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(invoke())

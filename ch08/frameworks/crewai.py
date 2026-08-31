"""Chapter 08 — Knowledge Graphs as Memory — CrewAI port.

Ingest typed triples, query, walk neighbors, refuse execute().

One researcher-with-a-store is a costume. One tool-bearing agent, or no crew.

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
sys.path.insert(0, str(_ROOT / "ch08" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from triple_store import TripleStore
from crewai import Agent, Crew, Process, Task
from runtime import homework_crew, run_crew


def build():
    _ = (Agent, Task, Process)
    return homework_crew(
        role="ch08 engineer",
        goal="Ingest typed triples, query, walk neighbors, refuse execute().",
        description="Ingest typed triples, query, walk neighbors, refuse execute().",
        fn=run,
    )


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
    return run_crew(build(), inputs)


if __name__ == "__main__":
    print(invoke())

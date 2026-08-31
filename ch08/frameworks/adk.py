"""Chapter 08 — Knowledge Graphs as Memory — Google ADK 2.0 port.

Ingest typed triples, query, walk neighbors, refuse execute().

G_K is a tool, not a Workflow. One memory-query node on G_A. execute() is TypeError.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch08" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from triple_store import TripleStore
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch08_worker",
        model="stub",
        instruction="Ingest typed triples, query, walk neighbors, refuse execute().",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch08_adk", sub_agents=[worker], description="G_K is a tool, not a Workflow. One memory-query node on G_A. execute() is TypeError.")


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


if __name__ == "__main__":
    print(build().run(None))

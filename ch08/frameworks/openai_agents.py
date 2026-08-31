"""Chapter 08 — Knowledge Graphs as Memory — OpenAI Agents SDK port.

Ingest typed triples, query, walk neighbors, refuse execute().

A store tool on one Agent. Do not hand off to a 'graph agent' that routes.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch08" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from triple_store import TripleStore
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch08_agent",
        instructions="Ingest typed triples, query, walk neighbors, refuse execute().",
        tools=[run],
        handoffs=[],
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


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(invoke())

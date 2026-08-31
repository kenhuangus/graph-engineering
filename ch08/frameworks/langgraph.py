"""Chapter 08 — Knowledge Graphs as Memory — LangGraph port.

Ingest typed triples, query, walk neighbors, refuse execute().

Topology: memory_query
Compiled StateGraph. Nodes are functions; the SDK owns the edges.

This file imports langgraph.graph.StateGraph / START / END.
compile().invoke() runs locally; no API key.
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
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("memory_query", lambda s, _n="memory_query": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge(START, "memory_query")
    g.add_edge("memory_query", END)
    return g.compile()


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
    print(run())

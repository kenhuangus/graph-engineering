"""Chapter 01 — The Week the Word Arrived — LangGraph port.

Reconstruct a directed naming graph from speech-act events.

Topology: ingest → emit_edges → report
Compiled StateGraph. Nodes are functions; the SDK owns the edges.

Live: `pip install langgraph` then swap the fallback StateGraph for
`from langgraph.graph import StateGraph, START, END`.
No API key is required for this deterministic port.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from runtime import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("ingest", lambda s, _n="ingest": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("emit_edges", lambda s, _n="emit_edges": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("report", lambda s, _n="report": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge("ingest", "emit_edges")
    g.add_edge("emit_edges", "report")
    g.add_edge(START, "ingest")
    g.add_edge("report", END)
    return g.compile()


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


if __name__ == "__main__":
    print(run())

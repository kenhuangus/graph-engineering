"""Chapter 01 — Graph Engineering Is Topology You Own — LangGraph port.

Reconstruct a directed naming graph from speech-act events.

Topology: ingest → emit_edges → report
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
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from langgraph.graph import END, START, StateGraph


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

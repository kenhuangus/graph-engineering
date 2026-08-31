"""Chapter 02 — Two Graphs, One Word — LangGraph port.

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

Topology: inspect → classify → halt
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
sys.path.insert(0, str(_ROOT / "ch02" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_kinds import GraphObject, classify
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("inspect", lambda s, _n="inspect": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("classify", lambda s, _n="classify": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("halt", lambda s, _n="halt": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge("inspect", "classify")
    g.add_edge("classify", "halt")
    g.add_edge(START, "inspect")
    g.add_edge("halt", END)
    return g.compile()


def run(obj=None):
    if obj is None:
        obj = GraphObject(
            name="refund-graph",
            node_kinds=("agent", "tool", "human"),
            edge_kinds=("unconditional", "conditional"),
            nodes_do_work=True,
            edges_are_facts=False,
            persists_beyond_run=False,
            is_one_run_recording=False,
            nodes_run=True,
        )
    return classify(obj)


if __name__ == "__main__":
    print(run())

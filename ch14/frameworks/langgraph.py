"""Chapter 14 — After the Word Dies — LangGraph port.

retirement_report: dead nodes, dead edges, candidates.

Topology: inventory
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
sys.path.insert(0, str(_ROOT / "ch14" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from retirement import GraphDecl, retirement_report
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("inventory", lambda s, _n="inventory": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge(START, "inventory")
    g.add_edge("inventory", END)
    return g.compile()


def run():
    spec = GraphDecl(
        nodes=("classify", "research", "specialist", "write", "halt"),
        edges=(
            ("classify", "research"),
            ("research", "write"),
            ("classify", "specialist"),
            ("specialist", "write"),
            ("write", "halt"),
        ),
        halt="halt",
    )
    traces = [
        ["classify", "research", "write", "halt"],
        ["classify", "research", "write", "halt"],
    ]
    return retirement_report(spec, traces)


if __name__ == "__main__":
    print(run())

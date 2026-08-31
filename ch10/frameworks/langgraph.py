"""Chapter 10 — The Computer Science Behind Graph Engineering — LangGraph port.

Kahn topological sort, cycle detection, ready-set on a diamond.

Topology: A → B → C → D
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
sys.path.insert(0, str(_ROOT / "ch10" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from kahn import has_cycle, ready_set, topological_sort
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("A", lambda s, _n="A": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("B", lambda s, _n="B": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("C", lambda s, _n="C": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("D", lambda s, _n="D": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    g.add_edge(START, "A")
    g.add_edge("D", END)
    return g.compile()


def run():
    nodes = ["A", "B", "C", "D"]
    diamond = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
    cycle = [("A", "B"), ("B", "C"), ("C", "A")]
    return {
        "order": topological_sort(nodes, diamond),
        "ready": sorted(ready_set(nodes, diamond, done={"A", "B"})),
        "cycle": has_cycle(["A", "B", "C"], cycle),
    }


if __name__ == "__main__":
    print(run())

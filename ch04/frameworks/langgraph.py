"""Chapter 04 — Anatomy of an Agent Graph — LangGraph port.

Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.

Topology: validate
Compiled StateGraph. Nodes are functions; the SDK owns the edges.

Live: `pip install langgraph` then swap the fallback StateGraph for
`from langgraph.graph import StateGraph, START, END`.
No API key is required for this deterministic port.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch04" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_spec import Edge, GraphSpec, Node, StateSchema, validate_spec
from runtime import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("validate", lambda s, _n="validate": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge(START, "validate")
    g.add_edge("validate", END)
    return g.compile()


def run(spec=None):
    if spec is None:
        spec = GraphSpec(
            nodes=(
                Node("scout", "agent"),
                Node("worker", "agent"),
                Node("review", "evaluator"),
                Node("human", "human"),
                Node("halt", "tool"),
            ),
            edges=(
                Edge("scout", "worker", "unconditional"),
                Edge("worker", "review", "unconditional"),
                Edge("review", "scout", "conditional", guard="verdict == fail AND n < 3"),
                Edge("review", "human", "conditional", guard="verdict == pass"),
                Edge("human", "halt", "unconditional"),
            ),
            state=StateSchema(fields={"draft": "str", "notes": "list"}, reducers={"notes": "append"}),
            halt_node="halt",
            human_interrupt="human",
        )
    return validate_spec(spec)


if __name__ == "__main__":
    print(run())

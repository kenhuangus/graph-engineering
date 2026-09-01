"""Chapter 13 — Testing, Evaluation, and Verification of Agent Graphs — LangGraph port.

check_trace: halt, join, unconstrained spend.

Topology: check
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
sys.path.insert(0, str(_ROOT / "ch13" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from trace_invariants import JoinSpec, TraceSpec, check_trace
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("check", lambda s, _n="check": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge(START, "check")
    g.add_edge("check", END)
    return g.compile()


def run():
    spec = TraceSpec(
        halt="halt",
        joins=(JoinSpec("research", ("web", "docs"), "write"),),
        gate_nodes=("human",),
        spend_nodes=("apply",),
    )
    good = check_trace(["web", "docs", "write", "human", "apply", "halt"], spec)
    bad = check_trace(["write", "apply", "halt"], spec)
    return {"good": [v.code for v in good], "bad": [v.code for v in bad]}


if __name__ == "__main__":
    print(run())

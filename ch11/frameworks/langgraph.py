"""Chapter 11 — Security, Identity, and Governance — LangGraph port.

Default-deny invoke, bound resume, cut-vertex reachability.

Topology: gate → spend
Compiled StateGraph. Nodes are functions; the SDK owns the edges.

Live: `pip install langgraph` then swap the fallback StateGraph for
`from langgraph.graph import StateGraph, START, END`.
No API key is required for this deterministic port.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch11" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from authz_graph import AuthzGraph, Principal
from runtime import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("gate", lambda s, _n="gate": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("spend", lambda s, _n="spend": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge("gate", "spend")
    g.add_edge(START, "gate")
    g.add_edge("spend", END)
    return g.compile()


def run():
    g = AuthzGraph(
        nodes=("start", "gate", "spend", "halt", "public"),
        edges=(("start", "gate"), ("gate", "spend"), ("spend", "halt"), ("start", "public"), ("public", "halt")),
        principals=(Principal("ken", "human"), Principal("stranger", "human")),
    )
    g.allow_invoke("ken", "spend")
    g.bind_resume("ken", "t1", "hash-a")
    return {
        "ken": g.can_invoke("ken", "spend"),
        "stranger": g.can_invoke("stranger", "spend"),
        "bad_resume": g.may_resume("ken", "t1", "hash-b"),
        "cut": g.is_cut_vertex("start", "spend", "gate"),
    }


if __name__ == "__main__":
    print(run())

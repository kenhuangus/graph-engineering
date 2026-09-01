"""Chapter 12 — Graph Intelligence Is Not the Runtime — LangGraph port.

One-layer message passing. This is G_L, not an agent graph.

Topology: message_pass
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
sys.path.insert(0, str(_ROOT / "ch12" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from message_passing import message_pass, normalize
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("message_pass", lambda s, _n="message_pass": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge(START, "message_pass")
    g.add_edge("message_pass", END)
    return g.compile()


def run():
    embeddings = {"a": [1.0, 0.0], "b": [0.0, 1.0], "c": [1.0, 0.0]}
    edges = [("a", "b")]
    out = message_pass(embeddings, edges, directed=False)
    isolated = normalize(embeddings["c"])
    return {"a": out["a"], "c": out["c"], "isolated": isolated, "moved": out["a"] != isolated}


if __name__ == "__main__":
    print(run())

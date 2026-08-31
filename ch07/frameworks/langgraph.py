"""Chapter 07 — Frameworks You Can Actually Ship On — LangGraph port.

Classify → research → write → review with a guarded back-edge.

Topology: classify → research → write → review
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
sys.path.insert(0, str(_ROOT / "ch07" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

import mini_stategraph as mini
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("classify", lambda s, _n="classify": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("research", lambda s, _n="research": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("write", lambda s, _n="write": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("review", lambda s, _n="review": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge("classify", "research")
    g.add_edge("research", "write")
    g.add_edge("write", "review")
    g.add_edge(START, "classify")
    g.add_edge("review", END)
    return g.compile()


def run(topic="loops vs graphs"):
    g = mini.StateGraph()
    g.add_node("classify", lambda s: {**s, "label": "research"})
    g.add_node("research", lambda s: {**s, "notes": (s.get("notes") or []) + [s["topic"]]})
    g.add_node("write", lambda s: {**s, "draft": "draft:" + ",".join(s.get("notes") or [])})
    def review(s):
        n = int(s.get("n", 0)) + 1
        return {**s, "n": n, "verdict": "pass" if n >= 1 else "revise"}
    g.add_node("review", review)
    g.add_edge(mini.START, "classify")
    g.add_edge("classify", "research")
    g.add_edge("research", "write")
    g.add_edge("write", "review")
    g.add_conditional_edges(
        "review",
        lambda s: "pass" if s.get("verdict") == "pass" else "revise",
        {"pass": mini.END, "revise": "write"},
    )
    g.add_reducer("notes", mini.append_list)
    return g.compile().invoke({"topic": topic, "notes": [], "n": 0})


if __name__ == "__main__":
    print(run())

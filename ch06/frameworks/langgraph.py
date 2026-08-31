"""Chapter 06 — Patterns That Earn Their Keep — LangGraph port.

Same job on sequential_path, supervisor_star, and fanout_join.

Topology: classify → research_web → research_docs → write
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
sys.path.insert(0, str(_ROOT / "ch06" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from pattern_runtime import fanout_join, make_job, sequential_path, supervisor_star
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("classify", lambda s, _n="classify": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("research_web", lambda s, _n="research_web": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("research_docs", lambda s, _n="research_docs": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_node("write", lambda s, _n="write": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge("classify", "research_web")
    g.add_edge("research_web", "research_docs")
    g.add_edge("research_docs", "write")
    g.add_edge(START, "classify")
    g.add_edge("write", END)
    return g.compile()


def run(pattern="sequential"):
    job = make_job()
    if pattern == "star":
        return supervisor_star(job)
    if pattern == "fanout":
        return fanout_join(job)
    return sequential_path(job)


if __name__ == "__main__":
    print(run())

"""Chapter 05 — When Not to Build a Graph — LangGraph port.

Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.

Topology: napkin
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
sys.path.insert(0, str(_ROOT / "ch05" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from napkin import JobSpec, napkin_test
from langgraph.graph import END, START, StateGraph


def build():
    g = StateGraph(dict)
    g.add_node("napkin", lambda s, _n="napkin": {**s, "visited": s.get("visited", []) + [_n]})
    g.add_edge(START, "napkin")
    g.add_edge("napkin", END)
    return g.compile()


def run(job=None):
    if job is None:
        job = JobSpec(workers=1, tools=("status_page",), fanout=False)
    return napkin_test(job)


if __name__ == "__main__":
    print(run())

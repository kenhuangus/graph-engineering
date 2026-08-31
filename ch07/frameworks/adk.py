"""Chapter 07 — Frameworks You Can Actually Ship On — Google ADK 2.0 port.

Classify → research → write → review with a guarded back-edge.

ADK 2.0 Workflow with a review → write back-edge and a halt. Wrappers until you need that edge.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file imports google.adk.Workflow. Function nodes run offline via InMemoryRunner; no Gemini key.
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
from google.adk import Workflow
from runtime import chapter_node, run_adk


def build():
    return Workflow(
        name="ch07_adk",
        description="ADK 2.0 Workflow with a review → write back-edge and a halt. Wrappers until you need that edge.",
        edges=[("START", chapter_node(run))],
    )


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
    print(run_adk(build()))

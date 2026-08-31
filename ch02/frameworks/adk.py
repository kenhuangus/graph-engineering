"""Chapter 02 — Two Graphs, One Word — Google ADK 2.0 port.

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

Single-turn LlmAgent is the wrong altitude. A Workflow node calls classify() and halt.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch02" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_kinds import GraphObject, classify
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch02_worker",
        model="stub",
        instruction="Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch02_adk", sub_agents=[worker], description="Single-turn LlmAgent is the wrong altitude. A Workflow node calls classify() and halt.")


def run(obj=None):
    if obj is None:
        obj = GraphObject(
            name="refund-graph",
            node_kinds=("agent", "tool", "human"),
            edge_kinds=("unconditional", "conditional"),
            nodes_do_work=True,
            edges_are_facts=False,
            persists_beyond_run=False,
            is_one_run_recording=False,
            nodes_run=True,
        )
    return classify(obj)


if __name__ == "__main__":
    print(build().run(None))

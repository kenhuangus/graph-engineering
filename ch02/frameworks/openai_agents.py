"""Chapter 02 — Two Graphs, One Word — OpenAI Agents SDK port.

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

One Agent, no handoff. Mash-up refusal is a guardrail, not a specialist.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch02" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_kinds import GraphObject, classify
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch02_agent",
        instructions="Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.",
        tools=[run],
        handoffs=[],
    )


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


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(invoke())

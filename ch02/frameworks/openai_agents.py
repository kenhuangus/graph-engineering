"""Chapter 02 — Execution Graphs and Memory Graphs — OpenAI Agents SDK port.

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

One Agent, no handoff. Mash-up refusal is a guardrail, not a specialist.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This file imports agents.Agent / Runner. A local Model subclass drives the tool loop; no OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch02" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_kinds import GraphObject, classify
from agents import Agent, Runner, handoff
from runtime import homework_openai_agent, run_openai


def build():
    _ = (Agent, Runner, handoff)
    return homework_openai_agent(
        name="ch02_agent",
        instructions="Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.",
        fn=run,
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
    return run_openai(build(), payload)


if __name__ == "__main__":
    print(invoke())

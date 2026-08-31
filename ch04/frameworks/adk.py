"""Chapter 04 — Anatomy of an Agent Graph — Google ADK 2.0 port.

Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.

Workflow node that admits or rejects a spec before any LlmAgent runs. compile() is the ADK analog.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch04" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_spec import Edge, GraphSpec, Node, StateSchema, validate_spec
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch04_worker",
        model="stub",
        instruction="Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch04_adk", sub_agents=[worker], description="Workflow node that admits or rejects a spec before any LlmAgent runs. compile() is the ADK analog.")


def run(spec=None):
    if spec is None:
        spec = GraphSpec(
            nodes=(
                Node("scout", "agent"),
                Node("worker", "agent"),
                Node("review", "evaluator"),
                Node("human", "human"),
                Node("halt", "tool"),
            ),
            edges=(
                Edge("scout", "worker", "unconditional"),
                Edge("worker", "review", "unconditional"),
                Edge("review", "scout", "conditional", guard="verdict == fail AND n < 3"),
                Edge("review", "human", "conditional", guard="verdict == pass"),
                Edge("human", "halt", "unconditional"),
            ),
            state=StateSchema(fields={"draft": "str", "notes": "list"}, reducers={"notes": "append"}),
            halt_node="halt",
            human_interrupt="human",
        )
    return validate_spec(spec)


if __name__ == "__main__":
    print(build().run(None))

"""Chapter 04 — Anatomy of an Agent Graph — OpenAI Agents SDK port.

Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.

Guardrail before Runner.run. An illegal spec never reaches a handoff.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch04" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_spec import Edge, GraphSpec, Node, StateSchema, validate_spec
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch04_agent",
        instructions="Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.",
        tools=[run],
        handoffs=[],
    )


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


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(run())

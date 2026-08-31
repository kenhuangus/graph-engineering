"""Chapter 04 — Anatomy of an Agent Graph — Anthropic Claude Agent SDK port.

Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies.

PreToolUse-style gate: validate_spec before any tool that spends.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch04" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_spec import Edge, GraphSpec, Node, StateSchema, validate_spec
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["graph_spec"], permission_mode="acceptEdits", model="stub")


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


def invoke(prompt: str = "Validate a GraphSpec: typed nodes, edges, S, halt, illegal topologies."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(invoke())

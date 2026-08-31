"""Chapter 02 — Two Graphs, One Word — Anthropic Claude Agent SDK port.

Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups.

query() plus a classify tool. The model does not get to rename the rooms.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch02" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from graph_kinds import GraphObject, classify
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["graph_kinds"], permission_mode="acceptEdits", model="stub")


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


def invoke(prompt: str = "Classify a GraphObject as G_A, G_K, or a run trace; refuse mash-ups."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(run())

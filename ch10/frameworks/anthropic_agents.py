"""Chapter 10 — The Computer Science Behind Graph Engineering — Anthropic Claude Agent SDK port.

Kahn topological sort, cycle detection, ready-set on a diamond.

query() is not Kahn. Python runs topological_sort; the SDK does not.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch10" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from kahn import has_cycle, ready_set, topological_sort
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["kahn"], permission_mode="acceptEdits", model="stub")


def run():
    nodes = ["A", "B", "C", "D"]
    diamond = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
    cycle = [("A", "B"), ("B", "C"), ("C", "A")]
    return {
        "order": topological_sort(nodes, diamond),
        "ready": sorted(ready_set(nodes, diamond, done={"A", "B"})),
        "cycle": has_cycle(["A", "B", "C"], cycle),
    }


def invoke(prompt: str = "Kahn topological sort, cycle detection, ready-set on a diamond."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(run())

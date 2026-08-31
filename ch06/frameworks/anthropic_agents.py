"""Chapter 06 — Patterns That Earn Their Keep — Anthropic Claude Agent SDK port.

Same job on sequential_path, supervisor_star, and fanout_join.

Three query() tools in a line, a hub tool for the star, parallel tools then synthesize for the join.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch06" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from pattern_runtime import fanout_join, make_job, sequential_path, supervisor_star
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["pattern_runtime"], permission_mode="acceptEdits", model="stub")


def run(pattern="sequential"):
    job = make_job()
    if pattern == "star":
        return supervisor_star(job)
    if pattern == "fanout":
        return fanout_join(job)
    return sequential_path(job)


def invoke(prompt: str = "Same job on sequential_path, supervisor_star, and fanout_join."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(invoke())

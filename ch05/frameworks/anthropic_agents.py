"""Chapter 05 — When Not to Build a Graph — Anthropic Claude Agent SDK port.

Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.

One query() loop. Three sequential queries is the bakeoff graph that did not earn its keep.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch05" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from napkin import JobSpec, napkin_test
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["napkin"], permission_mode="acceptEdits", model="stub")


def run(job=None):
    if job is None:
        job = JobSpec(workers=1, tools=("status_page",), fanout=False)
    return napkin_test(job)


def invoke(prompt: str = "Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(run())

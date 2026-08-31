"""Chapter 01 — The Week the Word Arrived — Anthropic Claude Agent SDK port.

Reconstruct a directed naming graph from speech-act events.

Claude Agent SDK query() with a single graph-assembly tool.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This file imports claude_agent_sdk.query / ClaudeAgentOptions. Live query() needs Claude CLI; homework invoke() type-checks the SDK objects then runs the chapter tool.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from claude_agent_sdk import ClaudeAgentOptions, query
from runtime import run_claude


def build():
    return ClaudeAgentOptions(allowed_tools=["naming_graph"], permission_mode="acceptEdits")


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


def invoke(prompt: str = "Reconstruct a directed naming graph from speech-act events."):
    return run_claude(query, build(), run, prompt)


if __name__ == "__main__":
    print(invoke())

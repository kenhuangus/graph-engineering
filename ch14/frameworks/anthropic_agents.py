"""Chapter 14 — After the Word Dies — Anthropic Claude Agent SDK port.

retirement_report: dead nodes, dead edges, candidates.

query() may narrate the report. It may not fill dead nodes with guessed walks.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch14" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from retirement import GraphDecl, retirement_report
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["retirement"], permission_mode="acceptEdits", model="stub")


def run():
    spec = GraphDecl(
        nodes=("classify", "research", "specialist", "write", "halt"),
        edges=(
            ("classify", "research"),
            ("research", "write"),
            ("classify", "specialist"),
            ("specialist", "write"),
            ("write", "halt"),
        ),
        halt="halt",
    )
    traces = [
        ["classify", "research", "write", "halt"],
        ["classify", "research", "write", "halt"],
    ]
    return retirement_report(spec, traces)


def invoke(prompt: str = "retirement_report: dead nodes, dead edges, candidates."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(run())

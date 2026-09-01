"""Chapter 14 — Keep the Graph After the Name Fades — Anthropic Claude Agent SDK port.

retirement_report: dead nodes, dead edges, candidates.

query() may narrate the report. It may not fill dead nodes with guessed walks.

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
sys.path.insert(0, str(_ROOT / "ch14" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from retirement import GraphDecl, retirement_report
from claude_agent_sdk import ClaudeAgentOptions, query
from runtime import run_claude


def build():
    return ClaudeAgentOptions(allowed_tools=["retirement"], permission_mode="acceptEdits")


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
    return run_claude(query, build(), run, prompt)


if __name__ == "__main__":
    print(invoke())

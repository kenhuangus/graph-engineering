"""Chapter 13 — Testing, Evaluation, and Verification — Anthropic Claude Agent SDK port.

check_trace: halt, join, unconstrained spend.

No query(). The checker is code.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch13" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from trace_invariants import JoinSpec, TraceSpec, check_trace
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["trace_invariants"], permission_mode="acceptEdits", model="stub")


def run():
    spec = TraceSpec(
        halt="halt",
        joins=(JoinSpec("research", ("web", "docs"), "write"),),
        gate_nodes=("human",),
        spend_nodes=("apply",),
    )
    good = check_trace(["web", "docs", "write", "human", "apply", "halt"], spec)
    bad = check_trace(["write", "apply", "halt"], spec)
    return {"good": [v.code for v in good], "bad": [v.code for v in bad]}


def invoke(prompt: str = "check_trace: halt, join, unconstrained spend."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(run())

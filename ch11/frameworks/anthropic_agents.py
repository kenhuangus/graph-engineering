"""Chapter 11 — Security, Identity, and Governance — Anthropic Claude Agent SDK port.

Default-deny invoke, bound resume, cut-vertex reachability.

Permission hook: deny if may_resume is false. Wrong hash is deny.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch11" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from authz_graph import AuthzGraph, Principal
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["authz_graph"], permission_mode="acceptEdits", model="stub")


def run():
    g = AuthzGraph(
        nodes=("start", "gate", "spend", "halt", "public"),
        edges=(("start", "gate"), ("gate", "spend"), ("spend", "halt"), ("start", "public"), ("public", "halt")),
        principals=(Principal("ken", "human"), Principal("stranger", "human")),
    )
    g.allow_invoke("ken", "spend")
    g.bind_resume("ken", "t1", "hash-a")
    return {
        "ken": g.can_invoke("ken", "spend"),
        "stranger": g.can_invoke("stranger", "spend"),
        "bad_resume": g.may_resume("ken", "t1", "hash-b"),
        "cut": g.is_cut_vertex("start", "spend", "gate"),
    }


def invoke(prompt: str = "Default-deny invoke, bound resume, cut-vertex reachability."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(invoke())

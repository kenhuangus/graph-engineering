"""Chapter 03 — Harness as Paradigm — Siblings, Not a Ladder — Anthropic Claude Agent SDK port.

Score a structured system against prompt / context / loop / graph / memory.

query() with a score_layers tool. Primary is argmax, not a vibe.

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
sys.path.insert(0, str(_ROOT / "ch03" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from five_layers import SystemDescription, score_layers
from claude_agent_sdk import ClaudeAgentOptions, query
from runtime import run_claude


def build():
    return ClaudeAgentOptions(allowed_tools=["five_layers"], permission_mode="acceptEdits")


def run(desc=None):
    if desc is None:
        desc = SystemDescription(
            has_system_prompt=True,
            single_turn=False,
            window_curation=False,
            retrieved_chunks_in_window=0,
            observe_act_verify=True,
            inner_loop_retries=2,
            tool_calls_inside_one_worker=True,
            named_nodes=(),
            named_edges=(),
            fan_out=False,
            join=False,
            halt_node=False,
            persistent_store=False,
            triple_retrieval=False,
            provenance_on_facts=False,
            entity_types=(),
        )
    return score_layers(desc)


def invoke(prompt: str = "Score a structured system against prompt / context / loop / graph / memory."):
    return run_claude(query, build(), run, prompt)


if __name__ == "__main__":
    print(invoke())

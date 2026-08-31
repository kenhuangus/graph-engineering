"""Chapter 08 — Knowledge Graphs as Memory — Anthropic Claude Agent SDK port.

Ingest typed triples, query, walk neighbors, refuse execute().

query() with ingest/query/neighbors tools. No Bash, no routing.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch08" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from triple_store import TripleStore
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["triple_store"], permission_mode="acceptEdits", model="stub")


def run(records=None):
    store = TripleStore()
    rows = records or [
        {"s": "redis", "p": "superseded_by", "o": "nats", "provenance": "adr-142"},
        {"s": "nats", "p": "used_by", "o": "payments-api", "provenance": "runbook"},
    ]
    store.ingest(rows)
    try:
        store.execute()
        execute = "called"
    except TypeError:
        execute = "refused"
    return {"count": len(store), "neighbors": sorted(store.neighbors("redis", depth=2)), "execute": execute}


def invoke(prompt: str = "Ingest typed triples, query, walk neighbors, refuse execute()."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(run())

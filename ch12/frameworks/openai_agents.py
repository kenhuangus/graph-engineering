"""Chapter 12 — Graph Intelligence — OpenAI Agents SDK port.

One-layer message passing. This is G_L, not an agent graph.

No agents. If you wrap this in Runner, you have costumed linear algebra.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch12" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from message_passing import message_pass, normalize
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch12_agent",
        instructions="One-layer message passing. This is G_L, not an agent graph.",
        tools=[run],
        handoffs=[],
    )


def run():
    embeddings = {"a": [1.0, 0.0], "b": [0.0, 1.0], "c": [1.0, 0.0]}
    edges = [("a", "b")]
    out = message_pass(embeddings, edges, directed=False)
    isolated = normalize(embeddings["c"])
    return {"a": out["a"], "c": out["c"], "isolated": isolated, "moved": out["a"] != isolated}


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(invoke())

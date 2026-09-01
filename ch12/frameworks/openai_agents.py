"""Chapter 12 — Graph Intelligence Is Not the Runtime — OpenAI Agents SDK port.

One-layer message passing. This is G_L, not an agent graph.

No agents. If you wrap this in Runner, you have costumed linear algebra.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This file imports agents.Agent / Runner. A local Model subclass drives the tool loop; no OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch12" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from message_passing import message_pass, normalize
from agents import Agent, Runner, handoff
from runtime import homework_openai_agent, run_openai


def build():
    _ = (Agent, Runner, handoff)
    return homework_openai_agent(
        name="ch12_agent",
        instructions="One-layer message passing. This is G_L, not an agent graph.",
        fn=run,
    )


def run():
    embeddings = {"a": [1.0, 0.0], "b": [0.0, 1.0], "c": [1.0, 0.0]}
    edges = [("a", "b")]
    out = message_pass(embeddings, edges, directed=False)
    isolated = normalize(embeddings["c"])
    return {"a": out["a"], "c": out["c"], "isolated": isolated, "moved": out["a"] != isolated}


def invoke(payload=None):
    return run_openai(build(), payload)


if __name__ == "__main__":
    print(invoke())

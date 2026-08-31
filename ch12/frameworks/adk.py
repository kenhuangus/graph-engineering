"""Chapter 12 — Graph Intelligence — Google ADK 2.0 port.

One-layer message passing. This is G_L, not an agent graph.

A single function node. Do not ParallelAgent the neighbors as workers.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch12" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from message_passing import message_pass, normalize
from runtime import LlmAgent, SequentialAgent, Workflow


def build():
    worker = LlmAgent(
        name="ch12_worker",
        model="stub",
        instruction="One-layer message passing. This is G_L, not an agent graph.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch12_adk", sub_agents=[worker], description="A single function node. Do not ParallelAgent the neighbors as workers.")


def run():
    embeddings = {"a": [1.0, 0.0], "b": [0.0, 1.0], "c": [1.0, 0.0]}
    edges = [("a", "b")]
    out = message_pass(embeddings, edges, directed=False)
    isolated = normalize(embeddings["c"])
    return {"a": out["a"], "c": out["c"], "isolated": isolated, "moved": out["a"] != isolated}


if __name__ == "__main__":
    print(build().run(None) if False else run())

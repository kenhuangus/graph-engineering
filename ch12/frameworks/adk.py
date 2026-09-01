"""Chapter 12 — Graph Intelligence Is Not the Runtime — Google ADK 2.0 port.

One-layer message passing. This is G_L, not an agent graph.

A single function node. Do not ParallelAgent the neighbors as workers.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file imports google.adk.Workflow. Function nodes run offline via InMemoryRunner; no Gemini key.
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
from google.adk import Workflow
from runtime import chapter_node, run_adk


def build():
    return Workflow(
        name="ch12_adk",
        description="A single function node. Do not ParallelAgent the neighbors as workers.",
        edges=[("START", chapter_node(run))],
    )


def run():
    embeddings = {"a": [1.0, 0.0], "b": [0.0, 1.0], "c": [1.0, 0.0]}
    edges = [("a", "b")]
    out = message_pass(embeddings, edges, directed=False)
    isolated = normalize(embeddings["c"])
    return {"a": out["a"], "c": out["c"], "isolated": isolated, "moved": out["a"] != isolated}


if __name__ == "__main__":
    print(run_adk(build()))

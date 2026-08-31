"""Chapter 03 — Harness as Paradigm — Siblings, Not a Ladder — Google ADK 2.0 port.

Score a structured system against prompt / context / loop / graph / memory.

One scoring node. Five SequentialAgents would imply a ladder this chapter refuses.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch03" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from five_layers import SystemDescription, score_layers
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch03_worker",
        model="stub",
        instruction="Score a structured system against prompt / context / loop / graph / memory.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch03_adk", sub_agents=[worker], description="One scoring node. Five SequentialAgents would imply a ladder this chapter refuses.")


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


if __name__ == "__main__":
    print(build().run(None))

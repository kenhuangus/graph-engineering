"""Chapter 03 — The Graph Under the Harness — Google ADK 2.0 port.

Score a structured system against prompt / context / loop / graph / memory.

One scoring node. Five SequentialAgents would imply a ladder this chapter refuses.

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
sys.path.insert(0, str(_ROOT / "ch03" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from five_layers import SystemDescription, score_layers
from google.adk import Workflow
from runtime import chapter_node, run_adk


def build():
    return Workflow(
        name="ch03_adk",
        description="One scoring node. Five SequentialAgents would imply a ladder this chapter refuses.",
        edges=[("START", chapter_node(run))],
    )


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
    print(run_adk(build()))

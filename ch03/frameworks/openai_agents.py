"""Chapter 03 — Harness as Paradigm — Siblings, Not a Ladder — OpenAI Agents SDK port.

Score a structured system against prompt / context / loop / graph / memory.

One Agent. Five handoffs, one per sibling, would treat siblings as a promotion path.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch03" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from five_layers import SystemDescription, score_layers
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch03_agent",
        instructions="Score a structured system against prompt / context / loop / graph / memory.",
        tools=[run],
        handoffs=[],
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


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(invoke())

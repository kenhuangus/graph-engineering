"""Chapter 03 — The Graph Under the Harness — OpenAI Agents SDK port.

Score a structured system against prompt / context / loop / graph / memory.

One Agent. Five handoffs, one per sibling, would treat siblings as a promotion path.

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
sys.path.insert(0, str(_ROOT / "ch03" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from five_layers import SystemDescription, score_layers
from agents import Agent, Runner, handoff
from runtime import homework_openai_agent, run_openai


def build():
    _ = (Agent, Runner, handoff)
    return homework_openai_agent(
        name="ch03_agent",
        instructions="Score a structured system against prompt / context / loop / graph / memory.",
        fn=run,
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
    return run_openai(build(), payload)


if __name__ == "__main__":
    print(invoke())

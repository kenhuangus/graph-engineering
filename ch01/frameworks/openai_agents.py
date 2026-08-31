"""Chapter 01 — The Week the Word Arrived — OpenAI Agents SDK port.

Reconstruct a directed naming graph from speech-act events.

One Agent with a tool that builds the graph. No handoff: there is no specialist to own the week.

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
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from agents import Agent, Runner, handoff
from runtime import homework_openai_agent, run_openai


def build():
    _ = (Agent, Runner, handoff)
    return homework_openai_agent(
        name="ch01_agent",
        instructions="Reconstruct a directed naming graph from speech-act events.",
        fn=run,
    )


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


def invoke(payload=None):
    return run_openai(build(), payload)


if __name__ == "__main__":
    print(invoke())

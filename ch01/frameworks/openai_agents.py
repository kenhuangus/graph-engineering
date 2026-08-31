"""Chapter 01 — The Week the Word Arrived — OpenAI Agents SDK port.

Reconstruct a directed naming graph from speech-act events.

One Agent with a tool that builds the graph. No handoff: there is no specialist to own the week.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch01_agent",
        instructions="Reconstruct a directed naming graph from speech-act events.",
        tools=[run],
        handoffs=[],
    )


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(invoke())

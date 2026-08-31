"""Chapter 05 — When Not to Build a Graph — OpenAI Agents SDK port.

Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.

One Agent, no handoffs. A manager with three specialist tools is the 3-node costume.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch05" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from napkin import JobSpec, napkin_test
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch05_agent",
        instructions="Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.",
        tools=[run],
        handoffs=[],
    )


def run(job=None):
    if job is None:
        job = JobSpec(workers=1, tools=("status_page",), fanout=False)
    return napkin_test(job)


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(run())

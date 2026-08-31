"""Chapter 06 — Patterns That Earn Their Keep — OpenAI Agents SDK port.

Same job on sequential_path, supervisor_star, and fanout_join.

Code-orchestrated sequential; manager.as_tool() for the star; asyncio-shaped fan-out for the join.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch06" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from pattern_runtime import fanout_join, make_job, sequential_path, supervisor_star
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch06_agent",
        instructions="Same job on sequential_path, supervisor_star, and fanout_join.",
        tools=[run],
        handoffs=[],
    )


def run(pattern="sequential"):
    job = make_job()
    if pattern == "star":
        return supervisor_star(job)
    if pattern == "fanout":
        return fanout_join(job)
    return sequential_path(job)


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(run())

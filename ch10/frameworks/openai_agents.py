"""Chapter 10 — The Computer Science Behind Graph Engineering — OpenAI Agents SDK port.

Kahn topological sort, cycle detection, ready-set on a diamond.

Code orchestration: asyncio-shaped B||C after A, then D. Handoffs cannot express a join.

Live: `pip install openai-agents` then
`from agents import Agent, Runner, handoff`.
This port uses a local Agent/Runner stand-in. No OpenAI key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch10" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from kahn import has_cycle, ready_set, topological_sort
from runtime import Agent, Runner


def build():
    return Agent(
        name="ch10_agent",
        instructions="Kahn topological sort, cycle detection, ready-set on a diamond.",
        tools=[run],
        handoffs=[],
    )


def run():
    nodes = ["A", "B", "C", "D"]
    diamond = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
    cycle = [("A", "B"), ("B", "C"), ("C", "A")]
    return {
        "order": topological_sort(nodes, diamond),
        "ready": sorted(ready_set(nodes, diamond, done={"A", "B"})),
        "cycle": has_cycle(["A", "B", "C"], cycle),
    }


def invoke(payload=None):
    return Runner.run_sync(build(), payload)


if __name__ == "__main__":
    print(run())

"""Chapter 06 — Patterns That Earn Their Keep — Google ADK 2.0 port.

Same job on sequential_path, supervisor_star, and fanout_join.

SequentialAgent for the path; ParallelAgent + join for fan-out; a coordinator LlmAgent for the star.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch06" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from pattern_runtime import fanout_join, make_job, sequential_path, supervisor_star
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch06_worker",
        model="stub",
        instruction="Same job on sequential_path, supervisor_star, and fanout_join.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch06_adk", sub_agents=[worker], description="SequentialAgent for the path; ParallelAgent + join for fan-out; a coordinator LlmAgent for the star.")


def run(pattern="sequential"):
    job = make_job()
    if pattern == "star":
        return supervisor_star(job)
    if pattern == "fanout":
        return fanout_join(job)
    return sequential_path(job)


if __name__ == "__main__":
    print(build().run(None))

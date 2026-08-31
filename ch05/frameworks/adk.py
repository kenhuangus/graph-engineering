"""Chapter 05 — When Not to Build a Graph — Google ADK 2.0 port.

Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.

LlmAgent / LoopAgent wrapper if the napkin says loop. Do not reach for Workflow of extract-draft-review.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch05" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from napkin import JobSpec, napkin_test
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch05_worker",
        model="stub",
        instruction="Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch05_adk", sub_agents=[worker], description="LlmAgent / LoopAgent wrapper if the napkin says loop. Do not reach for Workflow of extract-draft-review.")


def run(job=None):
    if job is None:
        job = JobSpec(workers=1, tools=("status_page",), fanout=False)
    return napkin_test(job)


if __name__ == "__main__":
    print(build().run(None))

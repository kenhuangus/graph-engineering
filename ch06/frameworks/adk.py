"""Chapter 06 — Patterns That Earn Their Nodes — Google ADK 2.0 port.

Same job on sequential_path, supervisor_star, and fanout_join.

SequentialAgent for the path; ParallelAgent + join for fan-out; a coordinator LlmAgent for the star.

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
sys.path.insert(0, str(_ROOT / "ch06" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from pattern_runtime import fanout_join, make_job, sequential_path, supervisor_star
from google.adk import Workflow
from runtime import chapter_node, run_adk


def build():
    return Workflow(
        name="ch06_adk",
        description="SequentialAgent for the path; ParallelAgent + join for fan-out; a coordinator LlmAgent for the star.",
        edges=[("START", chapter_node(run))],
    )


def run(pattern="sequential"):
    job = make_job()
    if pattern == "star":
        return supervisor_star(job)
    if pattern == "fanout":
        return fanout_join(job)
    return sequential_path(job)


if __name__ == "__main__":
    print(run_adk(build()))

"""Chapter 05 — When Not to Build a Graph — Google ADK 2.0 port.

Napkin test: stay on a loop or earn a graph. Sequential status copy stays a loop.

LlmAgent / LoopAgent wrapper if the napkin says loop. Do not reach for Workflow of extract-draft-review.

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
sys.path.insert(0, str(_ROOT / "ch05" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from napkin import JobSpec, napkin_test
from google.adk import Workflow
from runtime import chapter_node, run_adk


def build():
    return Workflow(
        name="ch05_adk",
        description="LlmAgent / LoopAgent wrapper if the napkin says loop. Do not reach for Workflow of extract-draft-review.",
        edges=[("START", chapter_node(run))],
    )


def run(job=None):
    if job is None:
        job = JobSpec(workers=1, tools=("status_page",), fanout=False)
    return napkin_test(job)


if __name__ == "__main__":
    print(run_adk(build()))

"""Chapter 06 — Patterns That Earn Their Nodes — CrewAI port.

Same job on sequential_path, supervisor_star, and fanout_join.

Process.sequential is the path. Process.hierarchical is the star. There is no join process — that is why Flows exist.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This file imports crewai.Agent / Task / Crew / Process. A BaseLLM subclass drives kickoff() offline; no provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
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
from crewai import Agent, Crew, Process, Task
from runtime import homework_crew, run_crew


def build():
    _ = (Agent, Task, Process)
    return homework_crew(
        role="ch06 engineer",
        goal="Same job on sequential_path, supervisor_star, and fanout_join.",
        description="Same job on sequential_path, supervisor_star, and fanout_join.",
        fn=run,
    )


def run(pattern="sequential"):
    job = make_job()
    if pattern == "star":
        return supervisor_star(job)
    if pattern == "fanout":
        return fanout_join(job)
    return sequential_path(job)


def invoke(inputs=None):
    return run_crew(build(), inputs)


if __name__ == "__main__":
    print(invoke())

"""Chapter 14 — After the Word Dies — Google ADK 2.0 port.

retirement_report: dead nodes, dead edges, candidates.

A query over declared edges vs traces. Not a Workflow that invents traffic.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch14" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from retirement import GraphDecl, retirement_report
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch14_worker",
        model="stub",
        instruction="retirement_report: dead nodes, dead edges, candidates.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch14_adk", sub_agents=[worker], description="A query over declared edges vs traces. Not a Workflow that invents traffic.")


def run():
    spec = GraphDecl(
        nodes=("classify", "research", "specialist", "write", "halt"),
        edges=(
            ("classify", "research"),
            ("research", "write"),
            ("classify", "specialist"),
            ("specialist", "write"),
            ("write", "halt"),
        ),
        halt="halt",
    )
    traces = [
        ["classify", "research", "write", "halt"],
        ["classify", "research", "write", "halt"],
    ]
    return retirement_report(spec, traces)


if __name__ == "__main__":
    print(build().run(None))

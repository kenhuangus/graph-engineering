"""Chapter 14 — Keep the Graph After the Name Fades — Google ADK 2.0 port.

retirement_report: dead nodes, dead edges, candidates.

A query over declared edges vs traces. Not a Workflow that invents traffic.

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
sys.path.insert(0, str(_ROOT / "ch14" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from retirement import GraphDecl, retirement_report
from google.adk import Workflow
from runtime import chapter_node, run_adk


def build():
    return Workflow(
        name="ch14_adk",
        description="A query over declared edges vs traces. Not a Workflow that invents traffic.",
        edges=[("START", chapter_node(run))],
    )


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
    print(run_adk(build()))

"""Chapter 01 — Graph Engineering Is Topology You Own — Google ADK 2.0 port.

Reconstruct a directed naming graph from speech-act events.

Workflow of ingest → classify_kind → emit_edge. This is G_naming, not a runtime.

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
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from google.adk import Workflow
from runtime import chapter_node, run_adk


def build():
    return Workflow(
        name="ch01_adk",
        description="Workflow of ingest → classify_kind → emit_edge. This is G_naming, not a runtime.",
        edges=[("START", chapter_node(run))],
    )


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


if __name__ == "__main__":
    print(run_adk(build()))

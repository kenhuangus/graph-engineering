"""Chapter 01 — The Week the Word Arrived — Google ADK 2.0 port.

Reconstruct a directed naming graph from speech-act events.

Workflow of ingest → classify_kind → emit_edge. This is G_naming, not a runtime.

Live: `pip install google-adk` and
`from google.adk import LlmAgent, Workflow` (2.0 Workflow Runtime, GA 19 May 2026).
This file runs the same topology with local stand-ins: no Gemini key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch01" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from naming_graph import Event, build_naming_graph, week_fixture
from runtime import LlmAgent, SequentialAgent


def build():
    worker = LlmAgent(
        name="ch01_worker",
        model="stub",
        instruction="Reconstruct a directed naming graph from speech-act events.",
        tools=[run],
        mode="single_turn",
    )
    return SequentialAgent(name="ch01_adk", sub_agents=[worker], description="Workflow of ingest → classify_kind → emit_edge. This is G_naming, not a runtime.")


def run(events=None):
    events = events if events is not None else week_fixture()
    return build_naming_graph(events)


if __name__ == "__main__":
    print(build().run(None))

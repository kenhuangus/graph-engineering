"""Chapter 07 — Frameworks You Can Actually Ship On — CrewAI port.

Classify → research → write → review with a guarded back-edge.

Sequential crew can do the happy path. A bounded review cycle is not Process.sequential — move to a graph or a Flow.

Live: `pip install crewai` then
`from crewai import Agent, Task, Crew, Process`.
This port uses local Crew/Task stand-ins. No provider key.
CrewAI Process is sequential | hierarchical only — no third "consensual" process.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch07" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

import mini_stategraph as mini
from runtime import Crew, CrewAgent, Process, Task


def build():
    agent = CrewAgent(
        role="ch07 engineer",
        goal="Classify → research → write → review with a guarded back-edge.",
        backstory="Deterministic stand-in. The topology is the lesson.",
        tools=[run],
    )
    task = Task(
        description="Classify → research → write → review with a guarded back-edge.",
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential)


def run(topic="loops vs graphs"):
    g = mini.StateGraph()
    g.add_node("classify", lambda s: {**s, "label": "research"})
    g.add_node("research", lambda s: {**s, "notes": (s.get("notes") or []) + [s["topic"]]})
    g.add_node("write", lambda s: {**s, "draft": "draft:" + ",".join(s.get("notes") or [])})
    def review(s):
        n = int(s.get("n", 0)) + 1
        return {**s, "n": n, "verdict": "pass" if n >= 1 else "revise"}
    g.add_node("review", review)
    g.add_edge(mini.START, "classify")
    g.add_edge("classify", "research")
    g.add_edge("research", "write")
    g.add_edge("write", "review")
    g.add_conditional_edges(
        "review",
        lambda s: "pass" if s.get("verdict") == "pass" else "revise",
        {"pass": mini.END, "revise": "write"},
    )
    g.add_reducer("notes", mini.append_list)
    return g.compile().invoke({"topic": topic, "notes": [], "n": 0})


def invoke(inputs=None):
    return build().kickoff(inputs)


if __name__ == "__main__":
    print(run())

"""Chapter 07 — Frameworks You Can Actually Ship On — Anthropic Claude Agent SDK port.

Classify → research → write → review with a guarded back-edge.

query() per node, Python owns the review back-edge budget. Sessions are not a checkpointer.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This file imports claude_agent_sdk.query / ClaudeAgentOptions. Live query() needs Claude CLI; homework invoke() type-checks the SDK objects then runs the chapter tool.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch07" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

import mini_stategraph as mini
from claude_agent_sdk import ClaudeAgentOptions, query
from runtime import run_claude


def build():
    return ClaudeAgentOptions(allowed_tools=["mini_stategraph"], permission_mode="acceptEdits")


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


def invoke(prompt: str = "Classify → research → write → review with a guarded back-edge."):
    return run_claude(query, build(), run, prompt)


if __name__ == "__main__":
    print(invoke())

"""Chapter 13 — Testing, Evaluation, and Verification of Agent Graphs — LangGraph port.

check_trace: halt, join, unconstrained spend.

Topology: (web, docs) fan-out -> write -> human -> apply -> halt
Compiled StateGraph. Nodes are functions; the SDK owns the edges.

The good walk is not typed by hand and not appended by the nodes: it is
derived from the runtime's own execution stream, which emits a node's name
only when that node actually fires. A node cannot write itself, or a gate,
into this record (ch. 11: the record belongs to the runtime, not to state).

This file imports langgraph.graph.StateGraph / START / END.
compile().stream() runs locally; no API key.
"""
from __future__ import annotations

import operator
import sys
from pathlib import Path
from typing import Annotated, TypedDict

_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _HERE]
sys.path.insert(0, str(_ROOT / "ch13" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from trace_invariants import JoinSpec, TraceSpec, check_trace
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    # The fan-out (web, docs) writes in one super-step, so the key needs
    # a reducer: the chapter's own fan-in rule. Note there is no trace key.
    notes: Annotated[list, operator.add]


def build():
    g = StateGraph(State)
    for name in ("web", "docs", "write", "human", "apply", "halt"):
        g.add_node(name, lambda s: {"notes": []})  # no trace bookkeeping
    g.add_edge(START, "web")
    g.add_edge(START, "docs")
    g.add_edge(["web", "docs"], "write")  # all-of join
    g.add_edge("write", "human")
    g.add_edge("human", "apply")
    g.add_edge("apply", "halt")
    g.add_edge("halt", END)
    return g.compile()


def runtime_walk(app) -> list[str]:
    """The walk as the scheduler saw it: one name per node that fired."""
    names: list[str] = []
    for update in app.stream({"notes": []}, stream_mode="updates"):
        names.extend(update.keys())
    return names


def run():
    spec = TraceSpec(
        halt="halt",
        joins=(JoinSpec("research", ("web", "docs"), "write"),),
        gate_nodes=("human",),
        spend_nodes=("apply",),
    )
    good = check_trace(runtime_walk(build()), spec)
    # The bad walk stays hand-typed on purpose: the compiled graph has no
    # path that skips the join and the gate, so no run can produce it. Only
    # a fabricated record can claim it, which is the reason to derive the
    # record from the runtime rather than from state a node could write.
    bad = check_trace(["write", "apply", "halt"], spec)
    return {"good": [v.code for v in good], "bad": [v.code for v in bad]}


if __name__ == "__main__":
    print(run())

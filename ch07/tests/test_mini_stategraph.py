from __future__ import annotations

import pytest

from mini_stategraph import (
    END,
    START,
    GraphCompileError,
    GraphRuntimeError,
    StateGraph,
    append_list,
)


def test_linear_graph_reducers_merge() -> None:
    g = StateGraph()
    g.add_node("a", lambda s: {"log": ["a"], "x": 1})
    g.add_node("b", lambda s: {"log": ["b"], "x": 2})
    g.add_reducer("log", append_list)
    g.add_edge(START, "a")
    g.add_edge("a", "b")
    g.add_edge("b", END)
    compiled = g.compile()
    out = compiled.invoke({"log": []})
    assert out["log"] == ["a", "b"]
    assert out["x"] == 2  # default reducer overwrites


def test_cycle_stops_at_n() -> None:
    N = 3

    def review(state: dict) -> dict:
        n = int(state.get("n", 0))
        if n >= N:
            return {"verdict": "pass"}
        return {"verdict": "revise"}

    def revise(state: dict) -> dict:
        return {"n": int(state.get("n", 0)) + 1, "draft": state.get("draft", "") + "x"}

    def route(state: dict) -> str:
        return "pass" if state.get("verdict") == "pass" else "again"

    g = StateGraph()
    g.add_node("review", review)
    g.add_node("revise", revise)
    g.add_edge(START, "review")
    g.add_conditional_edges("review", route, {"pass": END, "again": "revise"})
    g.add_edge("revise", "review")
    compiled = g.compile()
    out = compiled.invoke({"n": 0, "draft": ""})
    assert out["n"] == N
    assert out["verdict"] == "pass"
    assert out["draft"] == "x" * N


def test_unknown_node_compile_fails() -> None:
    g = StateGraph()
    g.add_node("only", lambda s: s)
    g.add_edge(START, "only")
    g.add_edge("only", "ghost")
    with pytest.raises(GraphCompileError):
        g.compile()


def test_unknown_conditional_destination_compile_fails() -> None:
    g = StateGraph()
    g.add_node("review", lambda s: {"verdict": "pass"})
    g.add_edge(START, "review")
    g.add_conditional_edges("review", lambda s: "pass", {"pass": "not_a_node"})
    with pytest.raises(GraphCompileError):
        g.compile()


def test_missing_entry_point_compile_fails() -> None:
    g = StateGraph()
    g.add_node("a", lambda s: {"ok": True})
    g.add_edge("a", END)
    with pytest.raises(GraphCompileError):
        g.compile()


def test_unguarded_cycle_hits_budget() -> None:
    g = StateGraph()
    g.add_node("ping", lambda s: {"n": int(s.get("n", 0)) + 1})
    g.add_node("pong", lambda s: {"n": int(s.get("n", 0)) + 1})
    g.add_edge(START, "ping")
    g.add_edge("ping", "pong")
    g.add_edge("pong", "ping")
    compiled = g.compile()
    with pytest.raises(GraphRuntimeError):
        compiled.invoke({"n": 0}, max_steps=8)

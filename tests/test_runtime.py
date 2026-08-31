"""Runtime stand-in tests. Collected because testpaths includes tests/."""
from __future__ import annotations

import pytest

from runtime import END, START, LlmAgent, StateGraph, _call_tool


def test_call_tool_omits_none_when_first_arg_has_default() -> None:
    calls: list[object] = []

    def run(topic: str = "good") -> str:
        calls.append(topic)
        if topic is None:
            raise TypeError("topic must not be None")
        return topic

    assert _call_tool(run, None) == "good"
    assert calls == ["good"]


def test_call_tool_does_not_swallow_inner_typeerror() -> None:
    def boom(payload=None):
        raise TypeError("inner failure")

    with pytest.raises(TypeError, match="inner failure"):
        _call_tool(boom, "x")


def test_call_tool_no_args() -> None:
    def run() -> str:
        return "ok"

    assert _call_tool(run, None) == "ok"


def test_llm_agent_run_none_uses_defaults() -> None:
    def run(topic: str = "loops vs graphs") -> dict:
        if topic is None:
            raise TypeError("None topic")
        return {"topic": topic}

    agent = LlmAgent(name="t", tools=[run])
    assert agent.run(None) == {"topic": "loops vs graphs"}


def test_stategraph_reducers_merge() -> None:
    def append_list(old, new):
        base = list(old) if old is not None else []
        return base + list(new)

    g = StateGraph(dict)
    g.add_node("a", lambda s: {"log": ["a"]})
    g.add_node("b", lambda s: {"log": ["b"]})
    g.add_reducer("log", append_list)
    g.add_edge(START, "a")
    g.add_edge("a", "b")
    g.add_edge("b", END)
    out = g.compile().invoke({"log": []})
    assert out["log"] == ["a", "b"]

"""Live SDK adapter tests. Skip when vendor packages are not installed."""
from __future__ import annotations

import importlib.util

import pytest

from runtime import _call_tool

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("langgraph") is None
    or importlib.util.find_spec("google.adk") is None
    or importlib.util.find_spec("agents") is None
    or importlib.util.find_spec("claude_agent_sdk") is None
    or importlib.util.find_spec("crewai") is None,
    reason="pip install -r requirements-frameworks.txt",
)


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


def test_langgraph_stategraph_is_vendor() -> None:
    from langgraph.graph import END, START, StateGraph

    g = StateGraph(dict)
    g.add_node("a", lambda s: {**s, "log": s.get("log", []) + ["a"]})
    g.add_node("b", lambda s: {**s, "log": s.get("log", []) + ["b"]})
    g.add_edge(START, "a")
    g.add_edge("a", "b")
    g.add_edge("b", END)
    out = g.compile().invoke({"log": []})
    assert out["log"] == ["a", "b"]


def test_adk_workflow_is_vendor() -> None:
    from google.adk import Workflow
    from runtime import chapter_node, run_adk

    def run() -> dict:
        return {"topic": "loops vs graphs"}

    wf = Workflow(name="t", description="offline", edges=[("START", chapter_node(run))])
    assert isinstance(wf, Workflow)
    assert run_adk(wf) == {"topic": "loops vs graphs"}


def test_openai_agent_is_vendor() -> None:
    from agents.agent import Agent
    from runtime import homework_openai_agent, run_openai

    def run(topic: str = "loops vs graphs") -> dict:
        if topic is None:
            raise TypeError("None topic")
        return {"topic": topic}

    agent = homework_openai_agent(name="t", instructions="offline", fn=run)
    assert isinstance(agent, Agent)
    assert run_openai(agent, None) == {"topic": "loops vs graphs"}

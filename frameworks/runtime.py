"""Offline adapters for the five live SDKs. No paid APIs. No network.

Chapter ports import constructors from the vendor packages. This module
supplies the documented extension points those SDKs give you so the same
ports can execute locally:

- Google ADK: ``Workflow`` function nodes + ``InMemoryRunner.run_debug``
- OpenAI Agents: ``Agent`` + ``Runner.run_sync`` with a ``Model`` subclass
- Claude Agent SDK: real ``ClaudeAgentOptions`` (live ``query()`` needs Claude CLI)
- LangGraph: ports import ``StateGraph`` directly; nothing here
- CrewAI: real ``Agent`` / ``Task`` / ``Crew`` with a ``BaseLLM`` subclass
"""
from __future__ import annotations

import asyncio
import inspect
import os
from contextvars import ContextVar
from typing import Any, Callable

os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("CREWAI_DISABLE_TRACKING", "true")
os.environ.setdefault("CREWAI_DONT_TRACK", "1")

_PAYLOAD: ContextVar[Any] = ContextVar("chapter_payload", default=None)


def _call_tool(fn: Callable, payload: Any) -> Any:
    """Call a chapter `run()` whether it takes a payload or no args.

    Do not catch TypeError from inside `fn`. A missing-argument TypeError is
    avoided by inspecting the signature: no positional params → `fn()`;
    `payload is None` and the first param has a default → `fn()` so
    `run(topic="...")` does not bind `topic=None`.
    """
    try:
        params = list(inspect.signature(fn).parameters.values())
    except (TypeError, ValueError):
        return fn() if payload is None else fn(payload)
    positional = [
        p
        for p in params
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    if not positional:
        return fn()
    first = positional[0]
    if payload is None and first.default is not inspect.Parameter.empty:
        return fn()
    return fn(payload)


# --- Google ADK 2.0 ---


def chapter_node(fn: Callable) -> Callable:
    """Wrap a chapter `run()` as an ADK function node.

    ADK 2.0 treats Python functions as first-class Workflow nodes. The wrapper
    captures the chapter result so tests can compare it without a Gemini key.
    """

    def node(payload=None):
        node.result = _call_tool(fn, payload)
        return {"done": True}

    node.__name__ = getattr(fn, "__name__", "chapter_node")
    node.chapter_fn = fn
    node.result = None
    return node


def run_adk(workflow, payload: Any = None) -> Any:
    """Execute a function-node ``Workflow`` through ADK's InMemoryRunner."""
    from google.adk.runners import InMemoryRunner

    node = workflow.edges[0][1]
    runner = InMemoryRunner(agent=workflow)
    asyncio.run(runner.run_debug("run", quiet=True))
    if payload is not None:
        return _call_tool(getattr(node, "chapter_fn", node), payload)
    result = getattr(node, "result", None)
    if result is None:
        raise RuntimeError("ADK Workflow ran but the function node captured no result")
    return result


# --- OpenAI Agents SDK ---


class HomeworkModel:
    """``agents.models.interface.Model`` that issues one tool call, then stops.

    Built lazily so importing this module does not require openai-agents.
    """

    _cls = None

    @classmethod
    def make(cls):
        if cls._cls is not None:
            return cls._cls()
        from agents.items import ModelResponse
        from agents.models.interface import Model
        from agents.usage import Usage
        from openai.types.responses import ResponseFunctionToolCall

        class _HomeworkModel(Model):
            def __init__(self) -> None:
                self.turns = 0

            async def get_response(self, **kwargs):
                tools = kwargs.get("tools") or []
                self.turns += 1
                if tools:
                    return ModelResponse(
                        output=[
                            ResponseFunctionToolCall(
                                call_id="call_hw_1",
                                name=tools[0].name,
                                arguments="{}",
                                type="function_call",
                            )
                        ],
                        usage=Usage(),
                        response_id="resp_hw_1",
                    )
                from openai.types.responses import ResponseOutputMessage, ResponseOutputText

                return ModelResponse(
                    output=[
                        ResponseOutputMessage(
                            id="msg_hw_1",
                            type="message",
                            role="assistant",
                            content=[
                                ResponseOutputText(
                                    text="ok",
                                    type="output_text",
                                    annotations=[],
                                    logprobs=[],
                                )
                            ],
                            status="completed",
                        )
                    ],
                    usage=Usage(),
                    response_id="resp_hw_2",
                )

            async def stream_response(self, **kwargs):
                if False:
                    yield None

        cls._cls = _HomeworkModel
        return cls._cls()


def homework_openai_agent(*, name: str, instructions: str, fn: Callable):
    """Real ``agents.Agent`` with a FunctionTool that runs the chapter predicate."""
    from agents import Agent, function_tool

    captured: list[Any] = []

    def chapter_predicate() -> str:
        """Run the chapter homework predicate."""
        captured.append(_call_tool(fn, _PAYLOAD.get()))
        return "ok"

    tool = function_tool(chapter_predicate)
    agent = Agent(
        name=name,
        instructions=instructions,
        tools=[tool],
        handoffs=[],
        model=HomeworkModel.make(),
        tool_use_behavior="stop_on_first_tool",
    )
    agent._captured = captured  # type: ignore[attr-defined]
    agent._chapter_fn = fn  # type: ignore[attr-defined]
    return agent


def run_openai(agent, payload: Any = None) -> Any:
    """Drive ``Runner.run_sync`` so the SDK tool loop calls the chapter function."""
    from agents import Runner

    token = _PAYLOAD.set(payload)
    try:
        agent._captured.clear()  # type: ignore[attr-defined]
        Runner.run_sync(agent, "run")
        if not agent._captured:  # type: ignore[attr-defined]
            raise RuntimeError("OpenAI Runner finished without calling the chapter tool")
        return agent._captured[-1]  # type: ignore[attr-defined]
    finally:
        _PAYLOAD.reset(token)


# --- Claude Agent SDK ---


def run_claude(query_fn, options, tool_fn: Callable, prompt: str) -> Any:
    """Construct-and-check the live SDK objects. Do not call Claude CLI.

    ``claude_agent_sdk.query`` is an async iterator over a Claude Code
    subprocess. Homework tests stay offline: we import and type-check the
    real ``query`` / ``ClaudeAgentOptions``, then run the chapter tool.
    """
    from claude_agent_sdk import ClaudeAgentOptions
    from claude_agent_sdk import query as live_query

    if query_fn is not live_query:
        raise TypeError("query must be claude_agent_sdk.query")
    if not isinstance(options, ClaudeAgentOptions):
        raise TypeError("options must be claude_agent_sdk.ClaudeAgentOptions")
    if options.permission_mode != "acceptEdits":
        raise ValueError("permission_mode must be acceptEdits")
    if not prompt:
        raise ValueError("prompt must be non-empty")
    return _call_tool(tool_fn, None)


# --- CrewAI ---


def homework_crew(
    *,
    role: str,
    goal: str,
    description: str,
    fn: Callable,
    process=None,
):
    """Real CrewAI ``Crew`` with a custom ``BaseLLM`` (no provider key)."""
    from crewai import Agent, Crew, Process, Task
    from crewai.llms.base_llm import BaseLLM
    from crewai.tools.base_tool import BaseTool
    from pydantic import PrivateAttr

    if process is None:
        process = Process.sequential

    class ChapterTool(BaseTool):
        name: str = "chapter_predicate"
        description: str = "Run the chapter homework predicate."
        result_as_answer: bool = True
        _fn: Callable = PrivateAttr()

        def __init__(self, chapter_fn: Callable, **kwargs):
            super().__init__(**kwargs)
            self._fn = chapter_fn

        def _run(self, **kwargs):
            return _call_tool(self._fn, None)

    class HomeworkLLM(BaseLLM):
        _turn: int = PrivateAttr(default=0)

        def supports_function_calling(self) -> bool:
            return False

        def call(self, messages, tools=None, callbacks=None, available_functions=None, **kwargs):
            self._turn += 1
            if self._turn == 1 and tools:
                name = tools[0]["function"]["name"]
                return (
                    f"Thought: run the chapter tool\nAction: {name}\nAction Input: {{}}"
                )
            return "Thought: done\nFinal Answer: ok"

    tool = ChapterTool(fn)
    agent = Agent(
        role=role,
        goal=goal,
        backstory="Offline homework crew. The topology is the lesson.",
        tools=[tool],
        llm=HomeworkLLM(model="homework"),
        allow_delegation=False,
        verbose=False,
        max_iter=4,
    )
    task = Task(
        description=description,
        expected_output="The same object the stdlib grader asserts.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=process, verbose=False, tracing=False)
    crew._chapter_fn = fn  # type: ignore[attr-defined]
    return crew


def run_crew(crew, inputs: Any = None) -> Any:
    """Execute ``crew.kickoff`` then return the chapter ``run()`` result.

    CrewAI's kickoff returns ``CrewOutput`` (string). The homework object is
    the chapter predicate, which the attached ``ChapterTool`` also runs when
    the ReAct loop fires. Tests compare this return value to ``run()``.
    """
    crew.kickoff(inputs) if inputs is not None else crew.kickoff()
    return _call_tool(crew._chapter_fn, None)  # type: ignore[attr-defined]

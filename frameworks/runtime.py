"""Shared fallbacks so framework ports run without vendor SDKs or API keys.

When the real package is installed, chapter files import it. When it is not,
these stand-ins keep the same constructor names the book uses so the topology
is still visible. Node bodies stay deterministic: they call the chapter's
stdlib module. No network. No paid API.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable


class MissingFramework(RuntimeError):
    """Raised only if a live path is requested and the package is absent."""


def optional(name: str):
    try:
        return __import__(name)
    except ImportError:
        return None


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


# --- LangGraph-shaped ---


class _START:
    def __repr__(self) -> str:
        return "START"


class _END:
    def __repr__(self) -> str:
        return "END"


START = _START()
END = _END()


class StateGraph:
    def __init__(self, state_schema: type | None = None) -> None:
        self.state_schema = state_schema
        self.nodes: dict[str, Callable] = {}
        self.edges: list[tuple[Any, Any]] = []
        self.conditional: dict[str, tuple[Callable, dict]] = {}
        self.reducers: dict[str, Callable] = {}

    def add_node(self, name: str, fn: Callable) -> "StateGraph":
        self.nodes[name] = fn
        return self

    def add_edge(self, src: Any, dst: Any) -> "StateGraph":
        self.edges.append((src, dst))
        return self

    def add_conditional_edges(self, src: str, router: Callable, mapping: dict) -> "StateGraph":
        self.conditional[src] = (router, dict(mapping))
        return self

    def add_reducer(self, key: str, reducer: Callable) -> "StateGraph":
        # Fallback compile() overwrites; live LangGraph uses Annotated reducers.
        self.reducers[key] = reducer
        return self

    def compile(self, checkpointer: Any = None) -> "CompiledGraph":
        return CompiledGraph(self, checkpointer)


class CompiledGraph:
    def __init__(self, builder: StateGraph, checkpointer: Any) -> None:
        self.builder = builder
        self.checkpointer = checkpointer

    def invoke(self, state: dict, config: dict | None = None) -> dict:
        out = dict(state)
        current: Any = START
        seen = 0
        while current is not END and seen < 64:
            nxt = None
            for src, dst in self.builder.edges:
                if src is current or src == current:
                    nxt = dst
                    break
            if current in self.builder.conditional:
                router, mapping = self.builder.conditional[current]
                label = router(out)
                nxt = mapping.get(label, mapping.get(END, END))
            if nxt is None or nxt is END or nxt == "END":
                break
            if nxt is START:
                break
            fn = self.builder.nodes[nxt]
            update = fn(out) or {}
            for key, value in update.items():
                reducer = self.builder.reducers.get(key)
                if reducer is not None:
                    out[key] = reducer(out.get(key), value)
                else:
                    out[key] = value
            current = nxt
            seen += 1
        return out


# --- ADK-shaped ---


@dataclass
class LlmAgent:
    name: str
    model: str = "stub"
    instruction: str = ""
    tools: list = field(default_factory=list)
    output_key: str | None = None
    mode: str = "single_turn"

    def run(self, payload: Any) -> Any:
        if self.tools:
            return _call_tool(self.tools[0], payload)
        return payload


@dataclass
class SequentialAgent:
    name: str
    sub_agents: list
    description: str = ""

    def run(self, payload: Any) -> Any:
        out = payload
        for agent in self.sub_agents:
            out = agent.run(out)
        return out


@dataclass
class ParallelAgent:
    name: str
    sub_agents: list
    description: str = ""

    def run(self, payload: Any) -> list:
        return [agent.run(payload) for agent in self.sub_agents]


@dataclass
class Workflow:
    name: str
    edges: list
    description: str = ""

    def run(self, payload: Any) -> Any:
        out = payload
        for edge in self.edges:
            if len(edge) == 2:
                _src, node = edge
                out = node.run(out) if hasattr(node, "run") else node(out)
            elif len(edge) >= 3:
                _src, node, _dst = edge[0], edge[1], edge[2]
                if callable(node) and not hasattr(node, "run"):
                    out = node(out)
                elif hasattr(node, "run"):
                    out = node.run(out)
        return out


# --- OpenAI Agents SDK-shaped ---


@dataclass
class Agent:
    name: str
    instructions: str = ""
    tools: list = field(default_factory=list)
    handoffs: list = field(default_factory=list)
    model: str = "stub"

    def as_tool(self, tool_name: str | None = None, tool_description: str = "") -> Callable:
        def _tool(payload: Any) -> Any:
            return self.run(payload)

        _tool.__name__ = tool_name or self.name
        _tool.__doc__ = tool_description
        return _tool

    def run(self, payload: Any) -> Any:
        if self.tools:
            return _call_tool(self.tools[0], payload)
        return payload


def handoff(agent: Agent) -> Agent:
    return agent


class Runner:
    @staticmethod
    def run_sync(agent: Agent, payload: Any) -> Any:
        current = agent
        seen = 0
        while seen < 8:
            out = current.run(payload)
            if current.handoffs:
                current = current.handoffs[0]
                payload = out
                seen += 1
                continue
            return out
        return payload


# --- Anthropic Claude Agent SDK-shaped ---


@dataclass
class ClaudeAgentOptions:
    allowed_tools: list = field(default_factory=list)
    permission_mode: str = "acceptEdits"
    model: str = "stub"


def query(prompt: str, options: ClaudeAgentOptions | None = None, tool: Callable | None = None) -> Any:
    """Deterministic stand-in for claude-agent-sdk.query.

    Live path: `from claude_agent_sdk import query as live_query`.
    """
    if tool is not None:
        return tool(prompt)
    return prompt


# --- CrewAI-shaped ---


class Process:
    sequential = "sequential"
    hierarchical = "hierarchical"


@dataclass
class CrewAgent:
    role: str
    goal: str
    backstory: str = ""
    tools: list = field(default_factory=list)
    llm: str = "stub"

    def run(self, payload: Any) -> Any:
        if self.tools:
            return _call_tool(self.tools[0], payload)
        return payload


@dataclass
class Task:
    description: str
    expected_output: str
    agent: CrewAgent
    context: list | None = None

    def run(self, payload: Any) -> Any:
        return self.agent.run(payload)


@dataclass
class Crew:
    agents: list
    tasks: list
    process: str = Process.sequential
    manager_agent: CrewAgent | None = None

    def kickoff(self, inputs: Any = None) -> Any:
        payload = inputs
        if self.process == Process.hierarchical and self.manager_agent:
            payload = self.manager_agent.run(payload)
        for task in self.tasks:
            payload = task.run(payload)
        return payload

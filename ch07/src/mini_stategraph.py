"""Chapter 7 — mini StateGraph. No LangGraph import. No HTTP.

Register nodes, edges, and reducers on a dict state. compile() validates.
invoke() runs until END or a step budget. A review→revise→review cycle is
legal when a guard (max N) stops it.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

START = "__start__"
END = "__end__"

Reducer = Callable[[Any, Any], Any]
NodeFn = Callable[[dict[str, Any]], dict[str, Any] | None]
RouterFn = Callable[[dict[str, Any]], str]


class GraphCompileError(ValueError):
    """Raised when compile() sees an unknown node or missing START."""


class GraphRuntimeError(RuntimeError):
    """Raised when invoke() hits a budget or an illegal router label."""


def overwrite(old: Any, new: Any) -> Any:
    return new


def append_list(old: Any, new: Any) -> Any:
    base = list(old) if old is not None else []
    if new is None:
        return base
    if isinstance(new, list):
        return base + new
    return base + [new]


class StateGraph:
    def __init__(self, state_keys: tuple[str, ...] | None = None) -> None:
        self.state_keys = state_keys
        self._nodes: dict[str, NodeFn] = {}
        self._edges: list[tuple[str, str]] = []
        self._conditional: dict[str, tuple[RouterFn, dict[str, str]]] = {}
        self._reducers: dict[str, Reducer] = {}

    def add_node(self, name: str, fn: NodeFn) -> None:
        if name in (START, END):
            raise GraphCompileError(f"{name} is reserved")
        if name in self._nodes:
            raise GraphCompileError(f"duplicate node {name!r}")
        self._nodes[name] = fn

    def add_edge(self, src: str, dst: str) -> None:
        self._edges.append((src, dst))

    def add_conditional_edges(self, src: str, router: RouterFn, mapping: Mapping[str, str]) -> None:
        self._conditional[src] = (router, dict(mapping))

    def add_reducer(self, key: str, reducer: Reducer) -> None:
        self._reducers[key] = reducer

    def set_entry_point(self, name: str) -> None:
        self.add_edge(START, name)

    def compile(self) -> "CompiledGraph":
        known = set(self._nodes) | {START, END}
        for src, dst in self._edges:
            if src not in known:
                raise GraphCompileError(f"edge source {src!r} is not a registered node")
            if dst not in known:
                raise GraphCompileError(f"edge destination {dst!r} is not a registered node")
        for src, (_router, mapping) in self._conditional.items():
            if src not in known:
                raise GraphCompileError(f"conditional source {src!r} is not a registered node")
            for label, dst in mapping.items():
                if dst not in known:
                    raise GraphCompileError(
                        f"conditional destination {dst!r} (label {label!r}) is not a registered node"
                    )
        if not any(src == START for src, _ in self._edges):
            raise GraphCompileError("no entry point: add_edge(START, first_node)")
        return CompiledGraph(
            nodes=dict(self._nodes),
            edges=list(self._edges),
            conditional=dict(self._conditional),
            reducers=dict(self._reducers),
        )


@dataclass
class CompiledGraph:
    nodes: dict[str, NodeFn]
    edges: list[tuple[str, str]]
    conditional: dict[str, tuple[RouterFn, dict[str, str]]]
    reducers: dict[str, Reducer]
    max_steps: int = 64

    def _unconditional_succ(self) -> dict[str, list[str]]:
        succ: dict[str, list[str]] = defaultdict(list)
        for src, dst in self.edges:
            succ[src].append(dst)
        return succ

    def _merge(self, state: dict[str, Any], update: Mapping[str, Any] | None) -> None:
        if not update:
            return
        for key, new in update.items():
            if key in self.reducers:
                state[key] = self.reducers[key](state.get(key), new)
            else:
                state[key] = new

    def invoke(self, initial: Mapping[str, Any] | None = None, *, max_steps: int | None = None) -> dict[str, Any]:
        budget = self.max_steps if max_steps is None else max_steps
        state: dict[str, Any] = dict(initial or {})
        succ = self._unconditional_succ()
        # Begin at START's successors. Sequential interpreter: one current node.
        starts = succ.get(START, [])
        if not starts:
            raise GraphRuntimeError("compiled graph has no START successor")
        current: str | None = starts[0]
        steps = 0
        while current is not None and current != END:
            if steps >= budget:
                raise GraphRuntimeError(f"halt budget exceeded ({budget}); cycle missing a guard?")
            fn = self.nodes.get(current)
            if fn is None:
                raise GraphRuntimeError(f"unknown node at runtime: {current!r}")
            update = fn(state) or {}
            self._merge(state, update)
            # Next hop: conditional router wins if registered, else unconditional edge.
            if current in self.conditional:
                router, mapping = self.conditional[current]
                label = router(state)
                if label not in mapping:
                    raise GraphRuntimeError(
                        f"router on {current!r} returned {label!r}, not in {sorted(mapping)}"
                    )
                nxt = mapping[label]
            else:
                dests = [d for d in succ.get(current, []) if True]
                if not dests:
                    nxt = END
                elif len(dests) == 1:
                    nxt = dests[0]
                else:
                    raise GraphRuntimeError(
                        f"node {current!r} has {len(dests)} unconditional successors; "
                        "use add_conditional_edges"
                    )
            current = None if nxt == END else nxt
            steps += 1
        return state

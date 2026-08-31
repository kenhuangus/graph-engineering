"""Chapter 4 — validate a GraphSpec before it is allowed to run.

A valid spec has typed nodes, directed typed edges, a shared state schema S,
a halt node, and an optional human-interrupt node. Illegal specs raise a
typed error, not a boolean.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterable, Literal, Mapping, Sequence

NODE_TYPES = frozenset({"agent", "tool", "evaluator", "human"})
EDGE_TYPES = frozenset({"unconditional", "conditional", "dynamic"})


class GraphSpecError(ValueError):
    """Base for all GraphSpec validation failures."""


class EmptyNodeSetError(GraphSpecError):
    """Raised when GraphSpec.nodes is empty."""


class MissingHaltError(GraphSpecError):
    """Raised when halt_node is missing from the node set."""


class UnknownNodeError(GraphSpecError):
    """Raised when an edge or interrupt names a missing node."""


class UnguardedCycleError(GraphSpecError):
    """Raised when a cycle has neither a halt node nor a guard."""


class UnknownNodeTypeError(GraphSpecError):
    """Raised when a node.type is not in the allowed set."""


class UnknownEdgeTypeError(GraphSpecError):
    """Raised when an edge.type is not in the allowed set."""


class EvaluatorWriteLockError(GraphSpecError):
    """Raised when an evaluator holds the write lock or a write tool."""


class UncappedSendError(GraphSpecError):
    """Raised when a dynamic Send edge has no send_cap on the source."""


class MixedRoutingError(GraphSpecError):
    """Raised when one node emits both a conditional map and a dynamic Send."""


class HumanAfterSideEffectError(GraphSpecError):
    """Raised when a human sits after an irreversible side-effect tool."""


class OverwriteFanInError(GraphSpecError):
    """Raised when a reducer overwrites a fan-in field."""


class OpenRouteMapError(GraphSpecError):
    """Raised when a model may mint a destination outside a closed map."""


WRITE_TOOLS = frozenset(
    {"issue_refund", "wire_payment", "apply_patch", "apply", "merge"}
)
SPEND_IDS = frozenset({"issue_refund", "apply", "apply_patch", "merge", "wire_payment"})


@dataclass(frozen=True)
class Node:
    id: str
    type: str  # agent | tool | evaluator | human
    tools: tuple[str, ...] = ()
    write_lock: bool = False
    send_cap: int | None = None
    destinations: tuple[str, ...] | None = None
    mint_destination: bool = False


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    type: str  # unconditional | conditional | dynamic
    guard: str | None = None
    destinations: tuple[str, ...] | None = None


@dataclass(frozen=True)
class StateSchema:
    fields: Mapping[str, str]
    reducers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphSpec:
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    state: StateSchema
    halt_node: str
    human_interrupt: str | None = None


def validate_spec(spec: GraphSpec) -> GraphSpec:
    """Return `spec` unchanged if it is legal; otherwise raise a typed error."""
    if not spec.nodes:
        raise EmptyNodeSetError("GraphSpec.nodes is empty")

    ids = [n.id for n in spec.nodes]
    id_set = set(ids)
    if len(ids) != len(id_set):
        raise GraphSpecError(f"duplicate node ids: {ids}")

    for n in spec.nodes:
        if n.type not in NODE_TYPES:
            raise UnknownNodeTypeError(f"node {n.id!r} has unknown type {n.type!r}")

    if spec.halt_node not in id_set:
        raise MissingHaltError(f"halt node {spec.halt_node!r} is not in the node set")

    if spec.human_interrupt is not None and spec.human_interrupt not in id_set:
        raise UnknownNodeError(
            f"human interrupt {spec.human_interrupt!r} is not in the node set"
        )

    for e in spec.edges:
        if e.type not in EDGE_TYPES:
            raise UnknownEdgeTypeError(f"edge {e.src}->{e.dst} has unknown type {e.type!r}")
        if e.src not in id_set:
            raise UnknownNodeError(f"edge source {e.src!r} is not a node")
        if e.dst not in id_set:
            raise UnknownNodeError(f"edge destination {e.dst!r} is not a node")

    _reject_unguarded_cycles(spec, id_set)
    _reject_anatomy(spec, {n.id: n for n in spec.nodes})
    return spec


def _is_side_effect(node: Node) -> bool:
    if node.write_lock:
        return True
    if node.id in SPEND_IDS:
        return True
    return bool(WRITE_TOOLS.intersection(node.tools))


def _reject_anatomy(spec: GraphSpec, by_id: dict[str, Node]) -> None:
    for n in spec.nodes:
        if n.type == "evaluator" and (n.write_lock or WRITE_TOOLS.intersection(n.tools)):
            raise EvaluatorWriteLockError(
                f"evaluator {n.id!r} holds the write lock or a write tool"
            )
        if n.mint_destination:
            raise OpenRouteMapError(
                f"node {n.id!r} may mint a destination outside a closed map"
            )

    succ = _successors(spec)
    for src, edges in succ.items():
        kinds = {e.type for e in edges}
        if "conditional" in kinds and "dynamic" in kinds:
            raise MixedRoutingError(
                f"node {src!r} mixes a conditional map with a dynamic Send"
            )
        src_node = by_id[src]
        for e in edges:
            if e.type == "dynamic" and not src_node.send_cap:
                raise UncappedSendError(
                    f"dynamic edge {e.src}->{e.dst} has no send_cap on {src!r}"
                )
            closed = e.destinations if e.destinations is not None else src_node.destinations
            if e.type == "conditional" and closed is not None and e.dst not in closed:
                raise OpenRouteMapError(
                    f"edge {e.src}->{e.dst} is not in the closed map {closed!r}"
                )
            dst = by_id.get(e.dst)
            if dst and dst.type == "human" and _is_side_effect(src_node):
                raise HumanAfterSideEffectError(
                    f"human {dst.id!r} sits after side-effect node {src!r}"
                )

    overwrite = {
        k for k, v in spec.state.reducers.items() if v in {"overwrite", "replace", "last_write"}
    }
    if overwrite:
        raise OverwriteFanInError(
            f"reducer overwrites fan-in field(s): {sorted(overwrite)}"
        )


def _successors(spec: GraphSpec) -> dict[str, list[Edge]]:
    succ: dict[str, list[Edge]] = defaultdict(list)
    for e in spec.edges:
        succ[e.src].append(e)
    return succ


def _simple_cycles(spec: GraphSpec, id_set: set[str]) -> list[list[str]]:
    """Enumerate simple directed cycles as lists of node ids (start == end omitted)."""
    succ = {n: [] for n in id_set}
    for e in spec.edges:
        succ[e.src].append(e.dst)

    cycles: list[list[str]] = []
    # Johnson-style DFS from each start, only walking to >= start to unique-ify.
    nodes = sorted(id_set)

    def dfs(start: str, node: str, trail: list[str], seen: set[str]) -> None:
        for nxt in succ[node]:
            if nxt < start:
                continue
            if nxt == start and len(trail) >= 1:
                cycles.append(trail[:] + [nxt])
                continue
            if nxt in seen:
                continue
            trail.append(nxt)
            seen.add(nxt)
            dfs(start, nxt, trail, seen)
            seen.remove(nxt)
            trail.pop()

    for start in nodes:
        dfs(start, start, [start], {start})
    return cycles


def _reject_unguarded_cycles(spec: GraphSpec, id_set: set[str]) -> None:
    """A cycle is legal iff it includes halt or at least one guarded edge."""
    succ_edges = _successors(spec)
    cycles = _simple_cycles(spec, id_set)
    for cyc in cycles:
        # cyc is [n0, n1, ..., n0]
        node_on_cycle = set(cyc)
        edges_on_cycle: list[Edge] = []
        for i in range(len(cyc) - 1):
            src, dst = cyc[i], cyc[i + 1]
            for e in succ_edges[src]:
                if e.dst == dst:
                    edges_on_cycle.append(e)
        has_guard = any(e.guard for e in edges_on_cycle)
        has_halt = spec.halt_node in node_on_cycle
        if not has_guard and not has_halt:
            raise UnguardedCycleError(
                f"cycle {cyc} has neither a halt node nor a guarded edge"
            )

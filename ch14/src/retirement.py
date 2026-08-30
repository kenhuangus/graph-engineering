"""Chapter 14 — retirement report.

A node that appears in the spec but never in any trace is dead.
An edge that is declared but never taken in any trace is dead.
Candidates are the dead nodes you could delete (everything dead except halt,
which is kept as the contract even if a malformed corpus missed it).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class GraphDecl:
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    halt: str = "halt"


@dataclass(frozen=True)
class RetirementReport:
    dead_nodes: tuple[str, ...]
    dead_edges: tuple[tuple[str, str], ...]
    live_nodes: tuple[str, ...]
    live_edges: tuple[tuple[str, str], ...]
    candidates: tuple[str, ...]  # dead nodes proposed for deletion


def _trace_nodes(trace: Sequence[str | dict]) -> list[str]:
    names: list[str] = []
    for item in trace:
        if isinstance(item, dict):
            names.append(str(item["node"]))
        else:
            names.append(str(item))
    return names


def _trace_edges(nodes_in_order: Sequence[str]) -> set[tuple[str, str]]:
    """Consecutive pairs in a single run. A taken edge is a hop the run actually made."""
    taken: set[tuple[str, str]] = set()
    for i in range(len(nodes_in_order) - 1):
        taken.add((nodes_in_order[i], nodes_in_order[i + 1]))
    return taken


def retirement_report(
    spec: GraphDecl,
    traces: Sequence[Sequence[str | dict]],
) -> RetirementReport:
    """Compare declared topology to observed traces.

    A live path (nodes and edges that appear) is kept. Unused specialist
    nodes and unused declared edges are listed.
    """
    declared_nodes = list(spec.nodes)
    declared_edges = list(spec.edges)
    declared_edge_set = set(declared_edges)

    seen_nodes: set[str] = set()
    taken_edges: set[tuple[str, str]] = set()
    for trace in traces:
        names = _trace_nodes(trace)
        seen_nodes.update(names)
        for hop in _trace_edges(names):
            if hop in declared_edge_set:
                taken_edges.add(hop)

    dead_nodes = tuple(n for n in declared_nodes if n not in seen_nodes)
    live_nodes = tuple(n for n in declared_nodes if n in seen_nodes)
    dead_edges = tuple(e for e in declared_edges if e not in taken_edges)
    live_edges = tuple(e for e in declared_edges if e in taken_edges)

    # Candidates: dead nodes other than halt (halt stays as the contract).
    candidates = tuple(n for n in dead_nodes if n != spec.halt)

    return RetirementReport(
        dead_nodes=dead_nodes,
        dead_edges=dead_edges,
        live_nodes=live_nodes,
        live_edges=live_edges,
        candidates=candidates,
    )

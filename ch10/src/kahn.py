"""Chapter 10 — Kahn's algorithm, cycle detection, ready set.

A diamond DAG: source → two middles → sink. Cycles are not sortable.
ready_set(done) is the nodes whose entire predecessor set is in `done`.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable, Sequence


class CycleError(ValueError):
    """Raised by topological_sort when the graph is not a DAG."""


def _build(
    nodes: Iterable[str],
    edges: Iterable[tuple[str, str]],
) -> tuple[list[str], dict[str, list[str]], dict[str, int], dict[str, set[str]]]:
    verts = list(dict.fromkeys(nodes))  # stable unique
    extra: set[str] = set()
    succ: dict[str, list[str]] = {v: [] for v in verts}
    preds: dict[str, set[str]] = {v: set() for v in verts}
    indeg: dict[str, int] = {v: 0 for v in verts}
    for u, v in edges:
        if u not in indeg:
            extra.add(u)
        if v not in indeg:
            extra.add(v)
        succ.setdefault(u, []).append(v)
        preds.setdefault(v, set()).add(u)
        preds.setdefault(u, preds.get(u, set()))
        indeg[v] = indeg.get(v, 0) + 1
        indeg.setdefault(u, indeg.get(u, 0))
    if extra:
        raise KeyError(f"edge endpoint not in nodes: {sorted(extra)}")
    return verts, succ, indeg, preds


def has_cycle(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> bool:
    verts, succ, indeg, _preds = _build(nodes, edges)
    remaining = dict(indeg)
    q: deque[str] = deque([v for v in verts if remaining[v] == 0])
    seen = 0
    while q:
        u = q.popleft()
        seen += 1
        for v in succ[u]:
            remaining[v] -= 1
            if remaining[v] == 0:
                q.append(v)
    return seen != len(verts)


def topological_sort(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[str]:
    """Kahn's algorithm. Raises CycleError if a cycle exists.

    Ties among ready nodes are broken by the original `nodes` order so the
    sort is deterministic.
    """
    verts, succ, indeg, _preds = _build(nodes, edges)
    remaining = dict(indeg)
    ready = deque([v for v in verts if remaining[v] == 0])
    order: list[str] = []
    while ready:
        u = ready.popleft()
        order.append(u)
        # Newly-zero nodes, in original vertex order for determinism.
        newly: list[str] = []
        for v in succ[u]:
            remaining[v] -= 1
            if remaining[v] == 0:
                newly.append(v)
        newly.sort(key=lambda n: verts.index(n))
        ready.extend(newly)
    if len(order) != len(verts):
        raise CycleError("graph has a cycle; Kahn cannot sort it")
    return order


def ready_set(
    nodes: Iterable[str],
    edges: Iterable[tuple[str, str]],
    done: Iterable[str],
) -> set[str]:
    """Nodes not in `done` whose every predecessor is in `done` (or has none)."""
    verts, _succ, _indeg, preds = _build(nodes, edges)
    done_set = set(done)
    unknown = done_set - set(verts)
    if unknown:
        raise KeyError(f"done contains unknown nodes: {sorted(unknown)}")
    ready: set[str] = set()
    for v in verts:
        if v in done_set:
            continue
        if preds[v] <= done_set:
            ready.add(v)
    return ready

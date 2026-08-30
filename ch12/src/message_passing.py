"""Chapter 12 — one-layer message passing.

For each node: new embedding = normalize(self + sum(neighbors)).
Stdlib floats. Neighbors are the undirected adjacency (both ends of an edge).
An isolated node therefore becomes normalize(self).
"""
from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence

Vector = list[float]


def l2_norm(vec: Sequence[float]) -> float:
    return math.sqrt(sum(x * x for x in vec))


def normalize(vec: Sequence[float]) -> Vector:
    n = l2_norm(vec)
    if n == 0.0:
        return [0.0 for _ in vec]
    return [x / n for x in vec]


def add(a: Sequence[float], b: Sequence[float]) -> Vector:
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} vs {len(b)}")
    return [x + y for x, y in zip(a, b)]


def message_pass(
    embeddings: Mapping[str, Sequence[float]],
    edges: Iterable[tuple[str, str]],
    *,
    directed: bool = False,
) -> dict[str, Vector]:
    """One layer: new[v] = normalize(self[v] + sum(self[u] for u neighbor of v)).

    The neighbor *vectors* are the *current* (pre-update) embeddings.
    Isolated nodes: normalize(self).
    Unknown edge endpoints raise KeyError.
    """
    keys = list(embeddings)
    dim: int | None = None
    current: dict[str, Vector] = {}
    for k, vec in embeddings.items():
        v = [float(x) for x in vec]
        if dim is None:
            dim = len(v)
        elif len(v) != dim:
            raise ValueError(f"node {k!r} has dim {len(v)}, expected {dim}")
        current[k] = v

    adj: dict[str, set[str]] = {k: set() for k in current}
    for u, v in edges:
        if u not in current or v not in current:
            raise KeyError(f"edge {(u, v)!r} names a node without an embedding")
        adj[u].add(v)
        if not directed:
            adj[v].add(u)

    out: dict[str, Vector] = {}
    for node, self_vec in current.items():
        acc = list(self_vec)
        for nbr in adj[node]:
            acc = add(acc, current[nbr])
        out[node] = normalize(acc)
    return out

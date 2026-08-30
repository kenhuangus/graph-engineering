"""Chapter 11 — authorization graph.

Default deny. Invoke is an allowlist on (principal, node). Resume is bound
to the triple (principal, thread_id, graph_hash) — a wrong hash is a deny,
not a retry. Reachability on the execution graph does not leak across a
cut vertex: removing the cut disconnects the two sides.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Principal:
    name: str
    kind: str  # human | agent | service | tool


@dataclass(frozen=True)
class ResumeToken:
    principal: str
    thread_id: str
    graph_hash: str


class AuthzGraph:
    def __init__(
        self,
        nodes: Iterable[str],
        edges: Iterable[tuple[str, str]],
        principals: Iterable[Principal],
    ) -> None:
        self.nodes: set[str] = set(nodes)
        self.edges: set[tuple[str, str]] = set(edges)
        self.principals: dict[str, Principal] = {p.name: p for p in principals}
        self._can_invoke: set[tuple[str, str]] = set()  # (principal, node)
        self._resume: set[ResumeToken] = set()
        for u, v in self.edges:
            if u not in self.nodes or v not in self.nodes:
                raise KeyError(f"edge {(u, v)!r} names an unknown node")

    def allow_invoke(self, principal: str, node: str) -> None:
        if principal not in self.principals:
            raise KeyError(f"unknown principal {principal!r}")
        if node not in self.nodes:
            raise KeyError(f"unknown node {node!r}")
        self._can_invoke.add((principal, node))

    def bind_resume(self, principal: str, thread_id: str, graph_hash: str) -> ResumeToken:
        if principal not in self.principals:
            raise KeyError(f"unknown principal {principal!r}")
        token = ResumeToken(principal=principal, thread_id=thread_id, graph_hash=graph_hash)
        self._resume.add(token)
        return token

    def can_invoke(self, principal: str, node: str) -> bool:
        """Default deny. Unknown principal is deny, not an error."""
        if principal not in self.principals:
            return False
        if node not in self.nodes:
            return False
        return (principal, node) in self._can_invoke

    def may_resume(self, principal: str, thread_id: str, graph_hash: str) -> bool:
        """True only for the exact bound triple. Wrong hash is deny."""
        if principal not in self.principals:
            return False
        token = ResumeToken(principal=principal, thread_id=thread_id, graph_hash=graph_hash)
        return token in self._resume

    def _succ(self, blocked: set[str] | None = None) -> dict[str, set[str]]:
        blocked = blocked or set()
        succ: dict[str, set[str]] = defaultdict(set)
        for u, v in self.edges:
            if u in blocked or v in blocked:
                continue
            succ[u].add(v)
        return succ

    def reachable(self, src: str, dst: str, *, blocked: Iterable[str] = ()) -> bool:
        """Directed reachability. Nodes in `blocked` are removed (cut)."""
        if src not in self.nodes or dst not in self.nodes:
            raise KeyError("src and dst must be nodes")
        blocked_set = set(blocked)
        if src in blocked_set or dst in blocked_set:
            return False
        succ = self._succ(blocked_set)
        seen = {src}
        q: deque[str] = deque([src])
        while q:
            u = q.popleft()
            if u == dst:
                return True
            for v in succ.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        return False

    def is_cut_vertex(self, src: str, dst: str, cut: str) -> bool:
        """True iff src reaches dst, but not after removing `cut`."""
        if cut in (src, dst):
            return False
        return self.reachable(src, dst) and not self.reachable(src, dst, blocked={cut})

"""Chapter 1 — reconstruct a directed naming graph from speech-act events.

Nodes are post ids. A quote-post or a reply creates a typed directed edge
from the target (the post being quoted or replied to) to the new post.
A bare `post` event contributes a node and no edge.

This is the object in Figure 1 of the book: a naming graph, not a runtime.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterable, Literal, Mapping, Sequence

EventKind = Literal["post", "quote_post", "reply"]
EdgeType = Literal["quote_post", "reply"]


@dataclass(frozen=True)
class Event:
    """One speech act in the naming week.

    `target_post_id` is required for quote_post and reply, and must be
    None for a bare post.
    """

    actor: str
    post_id: str
    kind: EventKind
    target_post_id: str | None = None
    timestamp: str = ""


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    edge_type: EdgeType


@dataclass
class NamingGraph:
    nodes: set[str]
    edges: tuple[Edge, ...]
    in_degree: dict[str, int]
    out_degree: dict[str, int]
    wcc_sizes: list[int]  # weakly-connected component sizes, descending

    def has_edge(self, src: str, dst: str, edge_type: str | None = None) -> bool:
        for e in self.edges:
            if e.src == src and e.dst == dst:
                if edge_type is None or e.edge_type == edge_type:
                    return True
        return False


def build_naming_graph(events: Sequence[Event]) -> NamingGraph:
    """Build the directed naming graph from an event list.

    Raises ValueError if a quote_post/reply is missing its target, or if a
    bare post carries a target.
    """
    if not events:
        return NamingGraph(nodes=set(), edges=(), in_degree={}, out_degree={}, wcc_sizes=[])

    nodes: set[str] = set()
    edges: list[Edge] = []
    seen_edge: set[tuple[str, str, str]] = set()

    for ev in events:
        if ev.kind not in ("post", "quote_post", "reply"):
            raise ValueError(f"unknown event kind: {ev.kind!r}")
        if not ev.post_id:
            raise ValueError("event is missing post_id")
        nodes.add(ev.post_id)
        if ev.target_post_id:
            nodes.add(ev.target_post_id)

        if ev.kind == "post":
            if ev.target_post_id is not None:
                raise ValueError(f"bare post {ev.post_id!r} must not name a target")
            continue

        if ev.target_post_id is None:
            raise ValueError(f"{ev.kind} {ev.post_id!r} is missing target_post_id")

        key = (ev.target_post_id, ev.post_id, ev.kind)
        if key in seen_edge:
            continue
        seen_edge.add(key)
        edges.append(Edge(src=ev.target_post_id, dst=ev.post_id, edge_type=ev.kind))  # type: ignore[arg-type]

    in_degree: dict[str, int] = {n: 0 for n in nodes}
    out_degree: dict[str, int] = {n: 0 for n in nodes}
    for e in edges:
        out_degree[e.src] = out_degree.get(e.src, 0) + 1
        in_degree[e.dst] = in_degree.get(e.dst, 0) + 1
        in_degree.setdefault(e.src, in_degree.get(e.src, 0))
        out_degree.setdefault(e.dst, out_degree.get(e.dst, 0))

    wcc_sizes = _wcc_sizes(nodes, edges)
    return NamingGraph(
        nodes=set(nodes),
        edges=tuple(edges),
        in_degree=in_degree,
        out_degree=out_degree,
        wcc_sizes=wcc_sizes,
    )


def _wcc_sizes(nodes: Iterable[str], edges: Sequence[Edge]) -> list[int]:
    """Weakly connected component sizes (ignore direction), descending."""
    adj: dict[str, set[str]] = defaultdict(set)
    node_set = set(nodes)
    for n in node_set:
        adj[n]  # ensure isolated nodes appear
    for e in edges:
        adj[e.src].add(e.dst)
        adj[e.dst].add(e.src)

    seen: set[str] = set()
    sizes: list[int] = []
    for start in node_set:
        if start in seen:
            continue
        q: deque[str] = deque([start])
        seen.add(start)
        size = 0
        while q:
            u = q.popleft()
            size += 1
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        sizes.append(size)
    sizes.sort(reverse=True)
    return sizes


def claimed_edge_in_events(
    events: Sequence[Event],
    src: str,
    dst: str,
    edge_type: str | None = None,
) -> bool:
    """Return True iff the claimed (src, dst[, type]) edge is implied by events.

    A claimed "Linear coincidence" edge that was never a quote-post or reply
    must return False. Presence of both nodes as independent posts is not
    an edge.
    """
    graph = build_naming_graph(events)
    return graph.has_edge(src, dst, edge_type)


def week_fixture() -> list[Event]:
    """Twelve speech-act events reconstructing the naming week (Figure 1).

    The Linear post is present as a node. There is no quote-post or reply
    connecting Steinberger's post to Linear — that dashed arrow is coincidence
    of naming, not a speech act.
    """
    S = "steinberger-2078277297791189132"
    return [
        Event(actor="steipete", post_id=S, kind="post", timestamp="2026-07-18T00:34:54Z"),
        Event(actor="Saboo", post_id="saboo-quote", kind="quote_post", target_post_id=S, timestamp="2026-07-18T02:10:05Z"),
        Event(actor="Husain", post_id="husain-article", kind="quote_post", target_post_id=S, timestamp="2026-07-18T05:09:36Z"),
        Event(actor="yoheinakajima", post_id="yohei-oops", kind="quote_post", target_post_id=S, timestamp="2026-07-18T05:19:20Z"),
        Event(actor="IntuitMachine", post_id="perez-from-loop", kind="reply", target_post_id=S, timestamp="2026-07-18T10:00:04Z"),
        Event(actor="DaleEverett", post_id="everett-shitty-graphs", kind="reply", target_post_id=S, timestamp="2026-07-19T22:25:05Z"),
        Event(actor="hwchase17", post_id="chase-langgraph", kind="quote_post", target_post_id=S, timestamp="2026-07-20T15:00:06Z"),
        Event(actor="shannholmberg", post_id="holmberg-who-decides", kind="reply", target_post_id="chase-langgraph", timestamp="2026-07-20T16:00:00Z"),
        Event(actor="DavidKPiano", post_id="dk-cyclic", kind="reply", target_post_id=S, timestamp="2026-07-20T17:00:00Z"),
        Event(actor="linear", post_id="linear-ships-loops", kind="post", timestamp="2026-07-20T18:00:00Z"),
        Event(actor="WalkingLabs", post_id="walkinglabs-recap", kind="reply", target_post_id="saboo-quote", timestamp="2026-07-21T12:00:00Z"),
        Event(actor="WECDocs", post_id="wecdocs-views", kind="quote_post", target_post_id="chase-langgraph", timestamp="2026-07-22T09:00:00Z"),
    ]


STEINBERGER_POST = "steinberger-2078277297791189132"
LINEAR_POST = "linear-ships-loops"

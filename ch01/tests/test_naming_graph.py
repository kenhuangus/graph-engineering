"""Grade the Chapter 1 naming-graph reconstruction.

The fixture is the naming week: twelve speech acts. Linear is a post with
no quote/reply to Steinberger. Tests fail if edges are invented, types are
dropped, or degrees ignore direction.
"""
from __future__ import annotations

import pytest

from naming_graph import (
    LINEAR_POST,
    STEINBERGER_POST,
    Event,
    build_naming_graph,
    claimed_edge_in_events,
)


def week_events() -> list[Event]:
    S = STEINBERGER_POST
    return [
        Event(actor="steipete", post_id=S, kind="post", timestamp="2026-07-18T00:34:54Z"),
        Event(actor="Saboo", post_id="saboo-quote", kind="quote_post", target_post_id=S),
        Event(actor="Husain", post_id="husain-article", kind="quote_post", target_post_id=S),
        Event(actor="yoheinakajima", post_id="yohei-oops", kind="quote_post", target_post_id=S),
        Event(actor="IntuitMachine", post_id="perez-from-loop", kind="reply", target_post_id=S),
        Event(actor="DaleEverett", post_id="everett-shitty-graphs", kind="reply", target_post_id=S),
        Event(actor="hwchase17", post_id="chase-langgraph", kind="quote_post", target_post_id=S),
        Event(actor="shannholmberg", post_id="holmberg-who-decides", kind="reply", target_post_id="chase-langgraph"),
        Event(actor="DavidKPiano", post_id="dk-cyclic", kind="reply", target_post_id=S),
        Event(actor="linear", post_id=LINEAR_POST, kind="post"),
        Event(actor="WalkingLabs", post_id="walkinglabs-recap", kind="reply", target_post_id="saboo-quote"),
        Event(actor="WECDocs", post_id="wecdocs-views", kind="quote_post", target_post_id="chase-langgraph"),
    ]


@pytest.fixture
def events() -> list[Event]:
    return week_events()


@pytest.fixture
def graph(events: list[Event]):
    return build_naming_graph(events)


def test_fixture_has_twelve_events(events: list[Event]) -> None:
    assert len(events) == 12


def test_edge_count_excludes_bare_posts(graph) -> None:
    # 10 quote/reply events → 10 edges. Two bare posts (Steinberger, Linear).
    assert len(graph.edges) == 10
    assert len(graph.nodes) == 12


def test_edge_types_preserved(graph) -> None:
    types = {(e.src, e.dst, e.edge_type) for e in graph.edges}
    assert (STEINBERGER_POST, "saboo-quote", "quote_post") in types
    assert (STEINBERGER_POST, "perez-from-loop", "reply") in types
    assert (STEINBERGER_POST, "everett-shitty-graphs", "reply") in types
    assert ("chase-langgraph", "holmberg-who-decides", "reply") in types
    assert ("chase-langgraph", "wecdocs-views", "quote_post") in types
    quote_count = sum(1 for e in graph.edges if e.edge_type == "quote_post")
    reply_count = sum(1 for e in graph.edges if e.edge_type == "reply")
    assert quote_count == 5
    assert reply_count == 5


def test_steinberger_degrees(graph) -> None:
    # Seven direct responses to the origin post; nothing points at it.
    assert graph.out_degree[STEINBERGER_POST] == 7
    assert graph.in_degree[STEINBERGER_POST] == 0
    assert graph.in_degree["chase-langgraph"] == 1
    assert graph.out_degree["chase-langgraph"] == 2
    assert graph.in_degree[LINEAR_POST] == 0
    assert graph.out_degree[LINEAR_POST] == 0


def test_linear_coincidence_edge_is_missing(events, graph) -> None:
    assert graph.has_edge(STEINBERGER_POST, LINEAR_POST) is False
    assert claimed_edge_in_events(events, STEINBERGER_POST, LINEAR_POST) is False
    # Both nodes exist; absence is about the edge, not the node.
    assert STEINBERGER_POST in graph.nodes
    assert LINEAR_POST in graph.nodes


def test_real_edge_is_present(events, graph) -> None:
    assert graph.has_edge(STEINBERGER_POST, "saboo-quote", "quote_post") is True
    assert claimed_edge_in_events(events, STEINBERGER_POST, "saboo-quote", "quote_post") is True
    assert claimed_edge_in_events(events, STEINBERGER_POST, "saboo-quote", "reply") is False


def test_weakly_connected_components_split_linear(graph) -> None:
    # One component of 11 (the speech-act cluster) and Linear isolated.
    assert graph.wcc_sizes == [11, 1]


def test_reply_without_target_raises() -> None:
    with pytest.raises(ValueError):
        build_naming_graph([Event(actor="x", post_id="p", kind="reply")])


def test_bare_post_with_target_raises() -> None:
    with pytest.raises(ValueError):
        build_naming_graph(
            [Event(actor="x", post_id="p", kind="post", target_post_id="other")]
        )

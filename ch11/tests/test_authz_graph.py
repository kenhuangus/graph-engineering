from __future__ import annotations

from authz_graph import AuthzGraph, Principal


def _graph() -> AuthzGraph:
    # Linear chain with a cut vertex: start → gate → spend → halt
    # A second branch start → public → halt  does not reach spend without gate.
    nodes = ("start", "gate", "spend", "public", "halt")
    edges = (
        ("start", "gate"),
        ("gate", "spend"),
        ("spend", "halt"),
        ("start", "public"),
        ("public", "halt"),
    )
    principals = (
        Principal("ken", "human"),
        Principal("refund-agent", "agent"),
        Principal("auditor", "human"),
    )
    g = AuthzGraph(nodes, edges, principals)
    g.allow_invoke("ken", "spend")
    g.allow_invoke("ken", "gate")
    g.allow_invoke("refund-agent", "public")
    g.bind_resume("ken", thread_id="thr-1", graph_hash="abc123")
    return g


def test_allowed_invoke() -> None:
    g = _graph()
    assert g.can_invoke("ken", "spend") is True
    assert g.can_invoke("ken", "gate") is True
    assert g.can_invoke("refund-agent", "public") is True


def test_unknown_principal_denied() -> None:
    g = _graph()
    assert g.can_invoke("stranger", "spend") is False
    assert g.can_invoke("stranger", "public") is False
    # Known principal, non-granted node: also deny (default deny).
    assert g.can_invoke("refund-agent", "spend") is False
    assert g.can_invoke("auditor", "gate") is False


def test_resume_wrong_hash_denied() -> None:
    g = _graph()
    assert g.may_resume("ken", "thr-1", "abc123") is True
    assert g.may_resume("ken", "thr-1", "WRONG") is False
    assert g.may_resume("ken", "thr-OTHER", "abc123") is False
    assert g.may_resume("refund-agent", "thr-1", "abc123") is False
    assert g.may_resume("stranger", "thr-1", "abc123") is False


def test_reachability_does_not_leak_across_cut_vertex() -> None:
    g = _graph()
    # spend is only reachable from start through gate.
    assert g.reachable("start", "spend") is True
    assert g.reachable("start", "spend", blocked={"gate"}) is False
    assert g.is_cut_vertex("start", "spend", "gate") is True
    # Removing gate must not invent a path via public.
    assert g.reachable("public", "spend") is False
    assert g.reachable("start", "halt", blocked={"gate"}) is True  # via public
    # public is NOT a cut between start and spend
    assert g.is_cut_vertex("start", "spend", "public") is False

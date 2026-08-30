from __future__ import annotations

from retirement import GraphDecl, retirement_report


SPEC = GraphDecl(
    nodes=("classify", "research", "specialist", "write", "halt"),
    edges=(
        ("classify", "research"),
        ("research", "write"),
        ("classify", "specialist"),
        ("specialist", "write"),
        ("write", "halt"),
    ),
    halt="halt",
)


def test_live_path_kept() -> None:
    traces = [
        ["classify", "research", "write", "halt"],
        ["classify", "research", "write", "halt"],
    ]
    report = retirement_report(SPEC, traces)
    for n in ("classify", "research", "write", "halt"):
        assert n in report.live_nodes
        assert n not in report.dead_nodes
    assert ("classify", "research") in report.live_edges
    assert ("research", "write") in report.live_edges
    assert ("write", "halt") in report.live_edges


def test_unused_specialist_node_listed() -> None:
    traces = [["classify", "research", "write", "halt"]]
    report = retirement_report(SPEC, traces)
    assert "specialist" in report.dead_nodes
    assert "specialist" in report.candidates
    assert "specialist" not in report.live_nodes
    # Halt is live here, so it is not a candidate.
    assert "halt" not in report.candidates
    assert "halt" not in report.dead_nodes


def test_unused_edge_listed() -> None:
    traces = [["classify", "research", "write", "halt"]]
    report = retirement_report(SPEC, traces)
    assert ("classify", "specialist") in report.dead_edges
    assert ("specialist", "write") in report.dead_edges
    assert ("classify", "specialist") not in report.live_edges
    assert ("research", "write") not in report.dead_edges


def test_empty_traces_everything_declared_is_dead() -> None:
    report = retirement_report(SPEC, traces=[])
    assert set(report.dead_nodes) == set(SPEC.nodes)
    assert set(report.dead_edges) == set(SPEC.edges)
    assert report.live_nodes == ()
    assert "specialist" in report.candidates
    # halt is dead-in-traces but not a deletion candidate
    assert "halt" not in report.candidates

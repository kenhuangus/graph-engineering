from __future__ import annotations

from trace_invariants import (
    HALT_NOT_REACHED,
    JOIN_INCOMPLETE,
    UNCONSTRAINED_SPEND,
    JoinSpec,
    TraceSpec,
    check_trace,
)


SPEC = TraceSpec(
    halt="halt",
    joins=(
        JoinSpec(
            name="research_join",
            required=("research_web", "research_docs"),
            downstream="write",
        ),
    ),
    gate_nodes=("gate",),
    spend_nodes=("spend",),
)


def test_good_trace_empty_violations() -> None:
    trace = [
        "classify",
        "research_web",
        "research_docs",
        "write",
        "gate",
        "spend",
        "halt",
    ]
    assert check_trace(trace, SPEC) == []


def test_missing_halt_fails() -> None:
    trace = ["classify", "research_web", "research_docs", "write", "gate", "spend"]
    viols = check_trace(trace, SPEC)
    codes = [v.code for v in viols]
    assert HALT_NOT_REACHED in codes
    halt = next(v for v in viols if v.code == HALT_NOT_REACHED)
    assert halt.node == "halt"


def test_skip_join_fails() -> None:
    # write runs after only one researcher
    trace = ["classify", "research_web", "write", "gate", "spend", "halt"]
    viols = check_trace(trace, SPEC)
    codes = [v.code for v in viols]
    assert JOIN_INCOMPLETE in codes
    join = next(v for v in viols if v.code == JOIN_INCOMPLETE)
    assert "research_docs" in join.message


def test_join_after_downstream_fails() -> None:
    # both researchers appear, but docs is after write
    trace = ["classify", "research_web", "write", "research_docs", "halt"]
    viols = check_trace(trace, SPEC)
    assert any(v.code == JOIN_INCOMPLETE for v in viols)


def test_spend_without_gate_fails() -> None:
    trace = ["classify", "research_web", "research_docs", "write", "spend", "halt"]
    viols = check_trace(trace, SPEC)
    codes = [v.code for v in viols]
    assert UNCONSTRAINED_SPEND in codes
    spend = next(v for v in viols if v.code == UNCONSTRAINED_SPEND)
    assert spend.node == "spend"


def test_dict_events_accepted() -> None:
    trace = [
        {"node": "classify"},
        {"node": "research_web"},
        {"node": "research_docs"},
        {"node": "write"},
        {"node": "gate"},
        {"node": "spend"},
        {"node": "halt"},
    ]
    assert check_trace(trace, SPEC) == []

from __future__ import annotations

import pytest

from graph_spec import (
    Edge,
    EmptyNodeSetError,
    EvaluatorWriteLockError,
    GraphSpec,
    HumanAfterSideEffectError,
    MissingHaltError,
    MixedRoutingError,
    Node,
    OpenRouteMapError,
    OverwriteFanInError,
    StateSchema,
    UncappedSendError,
    UnguardedCycleError,
    UnknownNodeError,
    validate_spec,
)

S = StateSchema(fields={"draft": "str", "notes": "list"}, reducers={"notes": "append"})


def _valid() -> GraphSpec:
    return GraphSpec(
        nodes=(
            Node("scout", "agent"),
            Node("worker", "agent"),
            Node("review", "evaluator"),
            Node("human", "human"),
            Node("halt", "tool"),
        ),
        edges=(
            Edge("scout", "worker", "unconditional"),
            Edge("worker", "review", "unconditional"),
            Edge("review", "scout", "conditional", guard="verdict == fail AND n < 3"),
            Edge("review", "human", "conditional", guard="verdict == pass"),
            Edge("human", "halt", "unconditional"),
        ),
        state=S,
        halt_node="halt",
        human_interrupt="human",
    )


def test_valid_spec_passes() -> None:
    spec = _valid()
    out = validate_spec(spec)
    assert out is spec
    assert out.halt_node == "halt"
    assert out.human_interrupt == "human"


def test_empty_node_set_raises() -> None:
    spec = GraphSpec(
        nodes=(),
        edges=(),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(EmptyNodeSetError):
        validate_spec(spec)


def test_missing_halt_raises() -> None:
    spec = GraphSpec(
        nodes=(Node("scout", "agent"), Node("worker", "agent")),
        edges=(Edge("scout", "worker", "unconditional"),),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(MissingHaltError):
        validate_spec(spec)


def test_edge_to_unknown_node_raises() -> None:
    spec = GraphSpec(
        nodes=(Node("scout", "agent"), Node("halt", "tool")),
        edges=(Edge("scout", "ghost", "unconditional"), Edge("scout", "halt", "unconditional")),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(UnknownNodeError):
        validate_spec(spec)


def test_unguarded_cycle_raises() -> None:
    spec = GraphSpec(
        nodes=(
            Node("a", "agent"),
            Node("b", "agent"),
            Node("halt", "tool"),
        ),
        edges=(
            Edge("a", "b", "unconditional"),
            Edge("b", "a", "unconditional"),  # cycle, no guard, halt not on cycle
            Edge("a", "halt", "unconditional"),
        ),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(UnguardedCycleError):
        validate_spec(spec)


def test_guarded_cycle_is_allowed() -> None:
    spec = GraphSpec(
        nodes=(
            Node("review", "evaluator"),
            Node("revise", "agent"),
            Node("halt", "tool"),
        ),
        edges=(
            Edge("review", "revise", "conditional", guard="verdict == revise AND n < 3"),
            Edge("revise", "review", "unconditional"),
            Edge("review", "halt", "conditional", guard="verdict == pass"),
        ),
        state=S,
        halt_node="halt",
    )
    assert validate_spec(spec).halt_node == "halt"


def test_evaluator_write_lock_raises() -> None:
    spec = GraphSpec(
        nodes=(
            Node("review", "evaluator", tools=("issue_refund",)),
            Node("halt", "tool"),
        ),
        edges=(Edge("review", "halt", "unconditional"),),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(EvaluatorWriteLockError):
        validate_spec(spec)


def test_uncapped_send_raises() -> None:
    spec = GraphSpec(
        nodes=(
            Node("dispatch", "tool"),
            Node("worker", "agent"),
            Node("halt", "tool"),
        ),
        edges=(
            Edge("dispatch", "worker", "dynamic"),
            Edge("worker", "halt", "unconditional"),
        ),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(UncappedSendError):
        validate_spec(spec)


def test_capped_send_is_allowed() -> None:
    spec = GraphSpec(
        nodes=(
            Node("dispatch", "tool", send_cap=8),
            Node("worker", "agent"),
            Node("halt", "tool"),
        ),
        edges=(
            Edge("dispatch", "worker", "dynamic"),
            Edge("worker", "halt", "unconditional"),
        ),
        state=S,
        halt_node="halt",
    )
    assert validate_spec(spec).halt_node == "halt"


def test_mixed_routing_raises() -> None:
    spec = GraphSpec(
        nodes=(
            Node("dispatch", "tool", send_cap=4),
            Node("worker", "agent"),
            Node("review", "evaluator"),
            Node("halt", "tool"),
        ),
        edges=(
            Edge("dispatch", "worker", "dynamic"),
            Edge("dispatch", "review", "conditional", guard="empty"),
            Edge("worker", "halt", "unconditional"),
            Edge("review", "halt", "unconditional"),
        ),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(MixedRoutingError):
        validate_spec(spec)


def test_human_after_side_effect_raises() -> None:
    spec = GraphSpec(
        nodes=(
            Node("apply", "tool", tools=("apply_patch",)),
            Node("human", "human"),
            Node("halt", "tool"),
        ),
        edges=(
            Edge("apply", "human", "unconditional"),
            Edge("human", "halt", "unconditional"),
        ),
        state=S,
        halt_node="halt",
        human_interrupt="human",
    )
    with pytest.raises(HumanAfterSideEffectError):
        validate_spec(spec)


def test_overwrite_fanin_raises() -> None:
    spec = GraphSpec(
        nodes=(Node("scout", "agent"), Node("halt", "tool")),
        edges=(Edge("scout", "halt", "unconditional"),),
        state=StateSchema(fields={"notes": "list"}, reducers={"notes": "overwrite"}),
        halt_node="halt",
    )
    with pytest.raises(OverwriteFanInError):
        validate_spec(spec)


def test_minted_destination_raises() -> None:
    spec = GraphSpec(
        nodes=(
            Node("router", "agent", mint_destination=True),
            Node("halt", "tool"),
        ),
        edges=(Edge("router", "halt", "unconditional"),),
        state=S,
        halt_node="halt",
    )
    with pytest.raises(OpenRouteMapError):
        validate_spec(spec)


def test_unknown_interrupt_node_raises() -> None:
    spec = GraphSpec(
        nodes=(Node("scout", "agent"), Node("halt", "tool")),
        edges=(Edge("scout", "halt", "unconditional"),),
        state=S,
        halt_node="halt",
        human_interrupt="missing_human",
    )
    with pytest.raises(UnknownNodeError):
        validate_spec(spec)

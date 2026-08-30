from __future__ import annotations

import pytest

from kahn import CycleError, has_cycle, ready_set, topological_sort

# Diamond: A → B, A → C, B → D, C → D
NODES = ("A", "B", "C", "D")
DIAMOND = (("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"))


def test_diamond_order_constraints() -> None:
    order = topological_sort(NODES, DIAMOND)
    assert set(order) == set(NODES)
    assert order[0] == "A"
    assert order.index("B") < order.index("D")
    assert order.index("C") < order.index("D")
    assert order.index("A") < order.index("B")
    assert order.index("A") < order.index("C")
    assert has_cycle(NODES, DIAMOND) is False


def test_cycle_detected_and_sort_raises() -> None:
    nodes = ("A", "B", "C")
    edges = (("A", "B"), ("B", "C"), ("C", "A"))
    assert has_cycle(nodes, edges) is True
    with pytest.raises(CycleError):
        topological_sort(nodes, edges)
    # A cycle plus a dangling source is still cyclic.
    nodes2 = ("S", "A", "B")
    edges2 = (("S", "A"), ("A", "B"), ("B", "A"))
    assert has_cycle(nodes2, edges2) is True
    with pytest.raises(CycleError):
        topological_sort(nodes2, edges2)


def test_ready_set_half_finished_diamond() -> None:
    # A and B done → C is ready (its only pred is A). D is not (C not done).
    ready = ready_set(NODES, DIAMOND, done={"A", "B"})
    assert ready == {"C"}
    # Only A done → both middles are ready, sink is not.
    assert ready_set(NODES, DIAMOND, done={"A"}) == {"B", "C"}
    # Nothing done → source only.
    assert ready_set(NODES, DIAMOND, done=set()) == {"A"}
    # All but sink → sink ready.
    assert ready_set(NODES, DIAMOND, done={"A", "B", "C"}) == {"D"}
    # All done → empty.
    assert ready_set(NODES, DIAMOND, done={"A", "B", "C", "D"}) == set()


def test_self_loop_is_a_cycle() -> None:
    assert has_cycle(("A",), (("A", "A"),)) is True
    with pytest.raises(CycleError):
        topological_sort(("A",), (("A", "A"),))

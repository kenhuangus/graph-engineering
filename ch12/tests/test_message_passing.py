from __future__ import annotations

import math

from message_passing import l2_norm, message_pass, normalize


def _close(a: list[float], b: list[float], tol: float = 1e-9) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))


def test_isolated_node_equals_normalized_self() -> None:
    self_vec = [3.0, 4.0]
    out = message_pass({"alone": self_vec, "other": [0.0, 1.0]}, edges=())
    expected = normalize(self_vec)
    assert out["alone"] == expected
    assert _close(out["alone"], [0.6, 0.8])
    assert _close(out["other"], [0.0, 1.0])


def test_isolated_is_unit_length() -> None:
    out = message_pass({"v": [3.0, 4.0]}, edges=())
    assert abs(l2_norm(out["v"]) - 1.0) < 1e-9
    assert _close(out["v"], [0.6, 0.8])


def test_node_with_neighbors_differs_from_isolated_copy() -> None:
    # Two copies of the same self-vector. One sits next to a neighbor,
    # the other is isolated. After one layer they must differ.
    embeddings = {
        "connected": [1.0, 0.0],
        "nbr": [0.0, 1.0],
        "isolated_copy": [1.0, 0.0],
    }
    edges = (("connected", "nbr"),)
    out = message_pass(embeddings, edges)
    assert not _close(out["connected"], out["isolated_copy"])
    # Isolated copy is normalize([1, 0]) = [1, 0]
    assert _close(out["isolated_copy"], [1.0, 0.0])
    # Connected: normalize([1,0] + [0,1]) = normalize([1,1])
    s = math.sqrt(2.0)
    assert _close(out["connected"], [1.0 / s, 1.0 / s])
    # Neighbor also aggregates the connected node.
    assert _close(out["nbr"], [1.0 / s, 1.0 / s])


def test_directed_neighbors_are_asymmetric() -> None:
    embeddings = {"a": [1.0, 0.0], "b": [0.0, 1.0]}
    out = message_pass(embeddings, edges=(("a", "b"),), directed=True)
    # a sees b; b does not see a.
    s = math.sqrt(2.0)
    assert _close(out["a"], [1.0 / s, 1.0 / s])
    assert _close(out["b"], [0.0, 1.0])

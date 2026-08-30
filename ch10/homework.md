# Chapter 10 — Computer Science (Kahn / DAG)

Implement the three functions a graph runtime is already using, whether it admits it or not.

## What you implement

Module: `kahn.py`.

- `has_cycle(nodes, edges) -> bool`
- `topological_sort(nodes, edges) -> list[str]` — Kahn's algorithm. Raise `CycleError` (a `ValueError`) on a cycle. Deterministic given `nodes` order.
- `ready_set(nodes, edges, done) -> set[str]` — nodes not in `done` whose **every** predecessor is in `done`.

The tests use a diamond: `A → B, A → C, B → D, C → D`.

- Source `A` is first; both middles precede the sink.
- A 3-cycle returns `True` from `has_cycle` and `topological_sort` raises.
- `ready_set` of a half-finished diamond (`done={A, B}`) is `{C}` — not `D`, not `A`.

## How to run

```bash
cd /workspace/book/homework
python -m pytest ch10 -v
```

## Done when

Diamond order constraints hold, cycles are refused, and the half-finished ready set is the other middle.

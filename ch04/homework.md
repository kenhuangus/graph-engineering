# Chapter 4 — Anatomy of an Agent Graph

Validate a `GraphSpec` before anyone runs it. A picture of boxes is not a spec.

## What you implement

Module: `graph_spec.py`.

Types:

- `Node(id, type)` with `type` in `{agent, tool, evaluator, human}`
- `Edge(src, dst, type, guard=None)` with `type` in `{unconditional, conditional, dynamic}`
- `StateSchema(fields, reducers)` — `S` is a contract, not a prompt
- `GraphSpec(nodes, edges, state, halt_node, human_interrupt=None)`

`validate_spec(spec) -> GraphSpec` returns the spec if legal.

Typed errors (subclasses of `GraphSpecError`):

| Situation | Error |
|-----------|--------|
| `nodes` is empty | `EmptyNodeSetError` |
| `halt_node` not in the node set | `MissingHaltError` |
| edge or interrupt names a node that does not exist | `UnknownNodeError` |
| a directed cycle with no `guard` on any cycle edge **and** halt not on the cycle | `UnguardedCycleError` |

A cycle that includes a guarded back-edge (review → revise → review with `n < N`) is legal. A two-node ping-pong with unconditional edges and halt sitting *off* the cycle is not.

## How to run

```bash
cd /workspace/book/homework
python -m pytest ch04 -v
```

## Done when

A valid spec (scout → worker → review ⇄ scout, then human → halt) passes. Each illegal case raises the typed error, not a generic `Exception`.

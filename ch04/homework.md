# Chapter 4 — Anatomy of an Agent Graph

Validate a `GraphSpec` before anyone runs it. A picture of boxes is not a spec. In the chapter, every vertex also names what it may read, what it may write, what done looks like as a machine-visible check, and a failure threshold. Those four fields are this assignment's typed errors in prose.

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
| evaluator holds `write_lock` or a write tool (`issue_refund`, `apply`, …) | `EvaluatorWriteLockError` |
| a `dynamic` Send edge whose source has no `send_cap` | `UncappedSendError` |
| one node emits both a conditional map and a dynamic Send | `MixedRoutingError` |
| a human sits after an irreversible side-effect tool | `HumanAfterSideEffectError` |
| a reducer overwrites a fan-in field (`overwrite` / `replace` / `last_write`) | `OverwriteFanInError` |
| a node may mint a destination outside a closed map | `OpenRouteMapError` |

A cycle that includes a guarded back-edge (review → revise → review with `n < N`) is legal. A two-node ping-pong with unconditional edges and halt sitting *off* the cycle is not. A reviewer that holds the write lock, a Send list with no cap, a mixed-routing node, a human after the side effect, an overwrite fan-in reducer, or a model allowed to mint a fifth destination is not.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/harness-eng
python -m pytest ch04 -v
```

## Done when

A valid spec (scout → worker → review ⇄ scout, then human → halt) passes. Each illegal case raises the typed error, not a generic `Exception`.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch04/frameworks/langgraph.py
```

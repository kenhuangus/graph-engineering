# Chapter 7 — Frameworks You Can Ship On

Build a **mini StateGraph**. No LangGraph. No HTTP. Dict state, registered nodes, edges, reducers, `compile()`, `invoke()`.

## What you implement

Module: `mini_stategraph.py`.

- Sentinels `START`, `END`
- `StateGraph` with `add_node`, `add_edge`, `add_conditional_edges`, `add_reducer`, `compile`
- `CompiledGraph.invoke(initial, *, max_steps=None) -> dict`
- `GraphCompileError` for unknown endpoints and a missing entry point
- `append_list` reducer (or equivalent) so two nodes writing the same list key **merge** rather than overwrite

Semantics:

1. `compile()` fails if any edge (unconditional or conditional mapping) names a node that was not registered, or if there is no `START` edge.
2. Default merge overwrites. A registered reducer receives `(old, new)`.
3. Conditional edges: the router sees the state *after* the node function merged, and returns a label in the mapping.
4. **Cycle with a halt/guard**: `review → revise → review` at most `N`. The guard is in the router / review node (e.g. `n >= N` routes to `END`). An unguarded ping-pong must not spin forever: `invoke(..., max_steps=K)` raises a runtime error when the budget is hit.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/harness-eng
python -m pytest ch07 -v
```

## Done when

Linear reducers merge to `["a", "b"]`; the review/revise cycle stops at `N`; unknown node compile-fails.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch07/frameworks/langgraph.py
```

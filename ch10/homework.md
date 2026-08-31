# Chapter 10 — Computer Science (Kahn / DAG)

Implement the three functions a graph runtime is already using, whether it admits it or not.

## What you implement

Module: `kahn.py`.

- `has_cycle(nodes, edges) -> bool`
- `topological_sort(nodes, edges) -> list[str]` — Kahn's algorithm. Raise `CycleError` (a `ValueError`) on a cycle. Deterministic given `nodes` order.
- `ready_set(nodes, edges, done) -> set[str]` — nodes not in `done` whose **every** predecessor is in `done`.

The in-chapter listing `chapter10_three_machines.py` is also in `src/`. It is not the assignment. Run it after the homework if you want the DAG / FSM / allowlist demo from the chapter.

The tests use a diamond: `A → B, A → C, B → D, C → D`.

- Source `A` is first; both middles precede the sink.
- A 3-cycle returns `True` from `has_cycle` and `topological_sort` raises.
- `ready_set` of a half-finished diamond (`done={A, B}`) is `{C}` — not `D`, not `A`.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/graph-engineering
python -m pytest ch10 -v
```

## Done when

Diamond order constraints hold, cycles are refused, and the half-finished ready set is the other middle.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch10/frameworks/langgraph.py
```

# Chapter 14 — Keep the Graph After the Name Fades

Retirement is a graph query, not a feeling. Compare the declared spec to the traces you actually ran.

## What you implement

Module: `retirement.py`.

- `GraphDecl(nodes, edges, halt="halt")`
- `RetirementReport(dead_nodes, dead_edges, live_nodes, live_edges, candidates)`
- `retirement_report(spec, traces) -> RetirementReport`

Definitions:

- A **dead node** appears in the spec and in **no** trace.
- A **dead edge** is declared and is never a consecutive hop in any trace (and that hop must be one of the declared edges).
- A **live** path is kept: those nodes/edges are *not* in the dead lists.
- **candidates** are dead nodes you could delete. Do not list `halt` as a candidate even if a corpus missed it — the halt contract stays.

The tests declare `classify → research → write → halt` plus an unused `specialist` branch `classify → specialist → write`. Traces only take the research path.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/graph-engineering
python -m pytest ch14 -v
```

## Done when

Live path kept; unused specialist listed as a dead node and a candidate; unused specialist edges listed as dead edges.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch14/frameworks/langgraph.py
```

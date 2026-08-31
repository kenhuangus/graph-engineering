# Chapter 2 — Two Graphs, One Word

The naming week used one English noun for three objects. Your job is to keep them in separate rooms.

## What you implement

Module: `graph_kinds.py`.

- `GraphObject` — structured fields (node kinds, edge kinds, flags). No NLP.
- `Classification(kind, name)` where `kind` is `execution_graph`, `knowledge_graph`, or `run_trace`.
- `MashupError(reason_code, message)` — a `ValueError` subclass with a closed reason code.
- `classify(obj: GraphObject) -> Classification`

Accept:

- **execution_graph (`G_A`)**: nodes do work (agent/tool/evaluator/human); edges are control flow; not a recording of one run; edges are not facts.
- **knowledge_graph (`G_K`)**: nodes are entities; edges are typed relations; persists beyond a run; nodes do not run.
- **run_trace**: one-run recording of what fired; does not persist as facts / memory.

Reject mash-ups with a `reason_code`. The tests include at least:

- a "workflow" whose edges are RDF relations → `workflow_with_rdf_edges`
- a KG whose nodes `nodes_run=True` → `kg_nodes_run`
- a trace that claims to persist as facts → `trace_claimed_as_memory`

You may add further reason codes; do not silently accept a mash-up as the nearest class.

## Constraints

Stdlib only. Decide from the fields, not from `name`. A record named `"kg"` that has agent nodes and control-flow edges is still `G_A` (or a mash-up), not a knowledge graph.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/harness-eng
python -m pytest ch02 -v
```

## Done when

Each clean class is accepted. At least three mash-up fixtures raise `MashupError` with the expected reason codes.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch02/frameworks/langgraph.py
```

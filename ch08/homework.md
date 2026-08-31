# Chapter 8 — Knowledge Graphs as Memory

A triple store is memory. It is not a workflow. Ingest facts, query them, walk neighbors, and refuse to `execute()`.

## What you implement

Module: `triple_store.py`.

- `Triple(s, p, o, provenance)`
- `TripleStore` with:
  - `ingest(records) -> int` — dicts with `s/p/o/provenance` (aliases `subject/predicate/object/source` ok). Provenance is required. Return count added; skip exact duplicates.
  - `query(s=None, p=None, o=None) -> list[Triple]` — `None` is a wildcard.
  - `neighbors(node, depth=1) -> set[str]` — undirected, depth 1 or 2, exclude the start node. Other depths raise `ValueError`.
  - `execute(*args, **kwargs)` — always raise `TypeError`. A knowledge graph does not run.

The in-chapter listing `memory_graph_node.py` is also in `src/`. It is not the assignment. It is the SQLite doorway (SHACL shapes, bi-temporal edges, one memory-query node) from the chapter.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/harness-eng
python -m pytest ch08 -v
```

## Done when

Ingest+query match bindings; provenance survives a re-ingest; a depth-2 walk from Redis reaches `payments-api`; `execute()` raises `TypeError`.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch08/frameworks/langgraph.py
```

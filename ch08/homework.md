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

## How to run

```bash
cd /workspace/book/homework
python -m pytest ch08 -v
```

## Done when

Ingest+query match bindings; provenance survives a re-ingest; a depth-2 walk from Redis reaches `payments-api`; `execute()` raises `TypeError`.

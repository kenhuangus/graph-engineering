# Chapter 11 — Security, Identity, Governance

An authorization graph is not a vibe. Default deny. Resume is a bound triple, not a courtesy.

## What you implement

Module: `authz_graph.py`.

- `Principal(name, kind)`
- `AuthzGraph(nodes, edges, principals)`
- `allow_invoke(principal, node)` — grant
- `can_invoke(principal, node) -> bool` — **default deny**. Unknown principal → `False` (not an exception).
- `bind_resume(principal, thread_id, graph_hash)`
- `may_resume(principal, thread_id, graph_hash) -> bool` — true only for the exact triple. Wrong hash is deny.
- `reachable(src, dst, *, blocked=()) -> bool` — directed reachability with nodes in `blocked` removed.
- `is_cut_vertex(src, dst, cut) -> bool` — src reaches dst, but not after removing `cut`.

The tests use `start → gate → spend → halt` plus `start → public → halt`. `gate` is a cut vertex on the path to `spend`. Removing it must not leak reachability through `public`.

## How to run

```bash
cd /workspace/book/homework
python -m pytest ch11 -v
```

## Done when

Ken can invoke `spend`; a stranger cannot; resume with the wrong hash is denied; `start` cannot reach `spend` with `gate` blocked.

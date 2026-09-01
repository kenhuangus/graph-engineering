# Chapter 11 — Security, Identity, and Governance of Agent Graphs

An authorization graph is not a vibe. Default deny. Resume is a bound triple, not a courtesy. Git worktrees are the filesystem cut vertex: a worker writes only in its tree; the join is a merge with a typed diff. Scoped tools are the same cut on the identity graph.

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

The in-chapter listing `chapter11_authz_reachability.py` is also in `src/`. It is not the assignment. It is the reachability checker from the chapter: ungated paths, blast radius, and the three fixtures.

The tests use `start → gate → spend → halt` plus `start → public → halt`. `gate` is a cut vertex on the path to `spend`. Removing it must not leak reachability through `public`.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/graph-engineering
python -m pytest ch11 -v
```

## Done when

Ken can invoke `spend`; a stranger cannot; resume with the wrong hash is denied; `start` cannot reach `spend` with `gate` blocked.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch11/frameworks/langgraph.py
```

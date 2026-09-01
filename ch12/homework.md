# Chapter 12 — Graph Intelligence Is Not the Runtime

One layer of message passing. No GPU. No numpy required. Stdlib floats.

## What you implement

Module: `message_passing.py`.

- `normalize(vec) -> list[float]` — L2 normalize; the zero vector stays zeros.
- `message_pass(embeddings, edges, *, directed=False) -> dict[str, list[float]]`

Update rule, one layer:

```
new[v] = normalize( self[v] + sum(self[u] for u in neighbors(v)) )
```

Neighbors are **undirected** by default (both ends of each edge). Pass `directed=True` to use out-neighbors only. Neighbor vectors are the *pre-update* embeddings. Isolated node: `normalize(self)`.

## Tests you must survive

- An isolated node's new embedding equals `normalize(self)` and has L2 length 1 (for a non-zero self).
- A node with a neighbor gets a **different** embedding than an isolated copy of the same self-vector.
- Directed mode is asymmetric: `a→b` updates `a` using `b`, not the other way around.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/graph-engineering
python -m pytest ch12 -v
```

## Done when

The isolated copy stays `[1, 0]` while the connected copy becomes the normalized sum with its neighbor.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch12/frameworks/langgraph.py
```

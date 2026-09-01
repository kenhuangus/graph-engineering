# Chapter 1 — Graph Engineering Is Topology You Own

Reconstruct the naming week as a **directed graph of speech acts**, not as a runtime.

On 18 July 2026 Steinberger posted twelve words. Quote-posts and replies followed. Linear shipped a product named "Loops" the same week; that is a coincidence of naming, not a quote or a reply. Your job is to turn a list of events into the graph and to be able to say, for any claimed edge, whether the event list actually contains it.

## What you implement

Module: `naming_graph.py` (this folder's `src/naming_graph.py` is the reference).

Public types and functions (type-hinted):

- `Event(actor, post_id, kind, target_post_id=None, timestamp="")`
  - `kind` is `"post"`, `"quote_post"`, or `"reply"`.
- `Edge(src, dst, edge_type)` with `edge_type` in `{quote_post, reply}`.
- `NamingGraph` with `nodes`, `edges`, `in_degree`, `out_degree`, `wcc_sizes`, and `has_edge(src, dst, edge_type=None)`.
- `build_naming_graph(events) -> NamingGraph`
- `claimed_edge_in_events(events, src, dst, edge_type=None) -> bool`

Rules:

1. Every event contributes its `post_id` as a node. A target id, if present, is also a node.
2. A `quote_post` or `reply` adds a directed edge **from the target to the new post**, typed with the event kind. Influence flows origin → response, matching Figure 1 in the chapter.
3. A bare `post` adds a node and no edge. If it carries a target, raise `ValueError`. If a quote/reply has no target, raise `ValueError`.
4. In-degree and out-degree are computed from those directed edges. Isolated nodes have degree 0.
5. `wcc_sizes` is the list of **weakly** connected component sizes (ignore direction), sorted descending.
6. `claimed_edge_in_events` is true only when a quote/reply in the list implies that edge. Two independent posts are not an edge.

## Fixture you must handle

Twelve events, including:

- Steinberger's origin post (`steinberger-2078277297791189132`).
- Quote-posts and replies that cluster around it (Saboo, Husain, Yohei, Perez, Everett, Chase, Khourshid, plus two second-hop responses).
- Linear's own post (`linear-ships-loops`) with **no** quote or reply linking it to Steinberger.

You may copy the ids from the tests; you must not invent an edge the events do not contain.

## Constraints

- Stdlib only. No network. No NLP. Events are already structured.
- Do not treat co-occurrence of names, timestamps, or topics as an edge.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/graph-engineering
python -m pytest ch01 -v
```

## Done when

All Chapter 1 tests pass: twelve events produce twelve nodes and ten typed edges; Steinberger's out-degree is the number of direct responses; the Linear coincidence is reported missing; weakly-connected sizes split Linear off the speech-act cluster.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch01/frameworks/langgraph.py
```

# Chapter 13 — Testing, Evaluation, and Verification of Agent Graphs

You are testing topology and contracts, not model quality. `check_trace(trace, spec)` returns the list of invariant violations. Specification drift is a legal-looking walk while the ticket is unmet: unit tests can stay green. Score the artifact against the spec, not only the node sequence.

## What you implement

Module: `trace_invariants.py`.

- `TraceSpec(halt, joins, gate_nodes, spend_nodes)`
- `JoinSpec(name, required, downstream)` — every name in `required` must appear **before** `downstream`.
- `Violation(code, message, node=None)`
- Codes: `halt_not_reached`, `join_incomplete`, `unconstrained_spend`
- `check_trace(trace, spec) -> list[Violation]`

Trace events may be node-name strings, dicts with a `"node"` key, or `TraceEvent` objects.

Invariants:

1. **Halt reached** — `spec.halt` appears in the trace.
2. **All-of join** — for each `JoinSpec`, if `downstream` ran, every `required` node ran strictly earlier.
3. **No unconstrained spend** — a spend node that appears must have at least one gate node in the prefix of the trace *before* it.

A good trace yields `[]`. Do not return a boolean.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/graph-engineering
python -m pytest ch13 -v
```

## Done when

Good trace: empty. Missing halt: `halt_not_reached`. Write without both researchers: `join_incomplete`. Spend with no prior gate: `unconstrained_spend`.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch13/frameworks/langgraph.py
```

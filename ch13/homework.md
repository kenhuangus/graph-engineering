# Chapter 13 — Testing, Evaluation, Verification

You are testing topology and contracts, not model quality. `check_trace(trace, spec)` returns the list of invariant violations.

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
cd /workspace/book/homework
python -m pytest ch13 -v
```

## Done when

Good trace: empty. Missing halt: `halt_not_reached`. Write without both researchers: `join_incomplete`. Spend with no prior gate: `unconstrained_spend`.

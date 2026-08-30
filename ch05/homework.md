# Chapter 5 — When Not to Build a Graph

The napkin test. Most jobs should stay on a loop. A graph has to earn each extra node.

## What you implement

Module: `napkin.py`.

- `JobSpec` — workers, tools, specialties, fanout flags, typed_handoffs, human_interrupt, halt_contract.
- `Decision(action, reasons)` — `action` is `stay_on_loop` or `build_graph`.
- Closed reason set: `needs_fanout`, `typed_handoff`, `human_interrupt`, `halt_contract`, `unknown_cardinality`.
- `napkin_test(job: JobSpec) -> Decision`

Rules the tests enforce:

1. **One worker plus tools**, no fan-out, no interrupt, no typed handoff, no halt-contract → `stay_on_loop` with empty reasons.
2. **Fan-out whose cardinality is unknown** at design time (`fanout=True`, `fanout_cardinality_known=False`) → `build_graph` and `unknown_cardinality` is among the reasons.
3. **Mixed case**: several specialties, known fan-out, typed handoffs, a human interrupt, a halt contract → `build_graph` with those reasons, and *not* `unknown_cardinality`.

Do not emit reasons outside the closed set.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/harness-eng
python -m pytest ch05 -v
```

## Done when

The three cases above (loop, unknown cardinality, mixed) pass, and every reason is in the closed set.

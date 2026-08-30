# Chapter 3 — The Five Layers

Prompt, context, loop, graph, and memory are **siblings** under harness engineering, not rungs on a replacement ladder. Score a *structured* system description (not free text) and report which layer is actually doing the work.

## What you implement

Module: `five_layers.py`.

- `SystemDescription` — booleans, counts, named nodes/edges, store flags. No NLP.
- `LayerScore(primary, scores)` — `primary` is one of `prompt|context|loop|graph|memory`; `scores` maps each layer to a float in `[0, 1]`.
- `score_layers(desc: SystemDescription) -> LayerScore`

Scoring must be a real function of the fields. Do not key off a fixture name. Suggested signals (you may weight them differently, but the tests' fixtures must come out right):

- **loop**: `observe_act_verify`, inner retries, tools inside one worker, ≤1 named node.
- **graph**: several named nodes, named edges, `fan_out`, `join`, `halt_node`.
- **memory**: `persistent_store`, `triple_retrieval`, provenance, entity types.
- **context**: window curation and retrieved chunks *without* a triple store.
- **prompt**: system prompt + single turn + no topology.

`primary` is argmax. Document a tie-break.

## Fixtures the tests use

1. A ReAct loop: one worker, observe-act-verify, retries, tools, no fan-out. **Loop must win.**
2. A fan-out DAG: plan → three workers → join → halt. **Graph must win.**
3. A triple-store RAG: persistent store, triple retrieval, provenance, entity types. **Memory must win.**

## How to run

```bash
cd /workspace/book/homework
python -m pytest ch03 -v
```

## Done when

The three fixtures pick the expected primary layer, and every score is inside `[0, 1]`.

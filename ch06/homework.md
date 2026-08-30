# Chapter 6 — Patterns That Earn Their Keep

A tiny in-memory runtime. No LLM. No HTTP. Three topologies on the **same** job.

The job: **classify**, two research workers (`research_web`, `research_docs`), then **write**.

## What you implement

Module: `pattern_runtime.py`.

- `Job(topic, label="", notes={}, document="")`
- `Message(src, dst, kind, body="")`
- `TraceEvent(node, superstep, pattern, notes_snapshot=())`
- `RunResult(pattern, job, trace, messages)`
- `make_job(topic="loops vs graphs") -> Job`
- `sequential_path(job) -> RunResult`
- `supervisor_star(job) -> RunResult`
- `fanout_join(job) -> RunResult`

Required behavior:

1. **sequential_path** — classify, then web, then docs, then write. Four distinct supersteps, that order.
2. **fanout_join** — classify in superstep 0; **both** researchers in the same later superstep; write in a later superstep still. Write's document must include both notes. If either note is missing, do not write (raise).
3. **supervisor_star** — a `supervisor` node is the hub. Workers (`classify`, `research_web`, `research_docs`, `write`) never send a `Message` to each other. Dispatch and report both go through supervisor.
4. The three traces/message lists are not interchangeable: sequential superstep occupancy differs from fan-out; supervisor messages differ from sequential.

Deterministic stand-in "workers" are fine (string formatting on `job.topic`). Do not `random.choice` a fake agent.

## How to run

```bash
cd /workspace/book/homework
python -m pytest ch06 -v
```

## Done when

Order constraints hold, the join is complete, the supervisor star has no worker-to-worker messages, and the three patterns disagree on their traces.

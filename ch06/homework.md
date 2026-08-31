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

The in-chapter listing `ch06_workers_messages.py` is also in `src/`. It is not the assignment. It is the claim-miner / skeptic / citation-scout message graph from the chapter.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/harness-eng
python -m pytest ch06 -v
```

## Done when

Order constraints hold, the join is complete, the supervisor star has no worker-to-worker messages, and the three patterns disagree on their traces.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch06/frameworks/langgraph.py
```

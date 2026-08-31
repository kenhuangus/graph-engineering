# Chapter 9 — Operating Graphs in Production

A step runner: retry, idempotency, circuit breaker. No network. Jitter and sleep are injected so tests do not wait on a wall clock. In the chapter, a coding graph in an existing repo is still this object: bounded retry on compile and tests, not on `apply_patch`; escalation is the interrupt or the open breaker.

## What you implement

Module: `step_runner.py`.

- `CircuitOpenError`
- `StepRunner(max_attempts, breaker_threshold, base_delay, sleep, rng, clock)`
- `run(fn, *, idempotency_key=None)`

Behavior:

1. **Retry.** Call `fn` up to `max_attempts`. On failure, sleep a jittered backoff `base_delay * 2^attempt * (0.5 + rng())` via the injected `sleep`. Do not call `time.sleep` if a `sleep` callable was provided — tests record delays.
2. **Idempotency.** If `idempotency_key` was already a *successful* run, return the cached result and do not call `fn` again. A duplicated delivery must not double a side effect.
3. **Circuit breaker.** Count failures (failed attempts). After `breaker_threshold` failures the breaker opens. Further `run` calls raise `CircuitOpenError` **without** calling `fn`. A success resets the failure streak.

## How to run

```bash
# from the repo root: https://github.com/kenhuangus/graph-engineering
python -m pytest ch09 -v
```

## Done when

A function that fails twice then succeeds returns `"ok"` within three attempts; a duplicate key increments a counter once; after K failures the next call is `CircuitOpenError` and the counter does not move.

## Framework ports

The graded module above is stdlib. The same predicate is also implemented with Google ADK 2.0, the OpenAI Agents SDK, the Anthropic Claude Agent SDK, LangGraph, and CrewAI in `frameworks/`. Those files call this chapter's `src/` module. No API keys. Default pytest does not collect them.

```bash
python ch09/frameworks/langgraph.py
```

"""Chapter 09 — Operating Graphs in Production — Anthropic Claude Agent SDK port.

Step runner: retry + jitter, idempotency, circuit breaker.

Hooks can deny a replay. The key still lives in your runner.

Live: `pip install claude-agent-sdk` then
`from claude_agent_sdk import query, ClaudeAgentOptions`.
This port uses a local query() stand-in. No Anthropic key.
The Agent SDK runs Claude Code's tool loop; the Messages API is a different package.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "ch09" / "src"))
sys.path.insert(0, str(_ROOT / "frameworks"))

from step_runner import CircuitOpenError, StepRunner
from runtime import ClaudeAgentOptions, query


def build():
    return ClaudeAgentOptions(allowed_tools=["step_runner"], permission_mode="acceptEdits", model="stub")


def run():
    box = {"n": 0}

    def flaky():
        box["n"] += 1
        if box["n"] < 3:
            raise RuntimeError("transient")
        return "ok"

    runner = StepRunner(max_attempts=3, breaker_threshold=5, base_delay=0, sleep=lambda _d: None, rng=lambda: 0.0)
    first = runner.run(flaky, idempotency_key="refund-1")
    second = runner.run(flaky, idempotency_key="refund-1")
    return {"first": first, "second": second, "calls": box["n"]}


def invoke(prompt: str = "Step runner: retry + jitter, idempotency, circuit breaker."):
    return query(prompt, options=build(), tool=lambda _p: run())


if __name__ == "__main__":
    print(run())

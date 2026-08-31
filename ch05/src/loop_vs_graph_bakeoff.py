#!/usr/bin/env python3
"""Loop vs 3-node graph bakeoff. Python 3.11+. No LLM required.

Chapter 5 of Graph Engineering. The job is sequential on purpose: turn a
short incident note into a customer status paragraph, then check a tiny
rubric. There is no independent fan-out. Token counts are word counts of
(system + user + completion) on each mock call.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

INCIDENT = (
    "At 14:12 UTC the payments-api in us-east-1 started returning 504s for "
    "about eleven minutes after a config push. Checkout was delayed, not "
    "lost. We rolled back the config at 14:23. A status page went up at "
    "14:18. Do not promise a restore time. Service name is payments-api."
)

RUBRIC = (
    "must name payments-api; must not promise a restore time or a date; "
    "must be under 80 words; must say checkout was delayed not lost"
)


def words(text: str) -> int:
    return len(text.split())


@dataclass
class CallLog:
    name: str
    system: str
    user: str
    completion: str
    ms: float

    @property
    def tokens(self) -> int:
        return words(self.system) + words(self.user) + words(self.completion)


@dataclass
class Run:
    arm: str
    output: str
    calls: list[CallLog] = field(default_factory=list)
    wall_ms: float = 0.0
    state_copies: int = 0

    @property
    def tokens(self) -> int:
        return sum(c.tokens for c in self.calls)

    @property
    def n_calls(self) -> int:
        return len(self.calls)


class MockLLM:
    """Deterministic stand-in. One sleep per call so wall-clock is a sum."""

    def __init__(self, latency_s: float = 0.02) -> None:
        self.latency_s = latency_s
        self.calls: list[CallLog] = []

    def complete(self, name: str, system: str, user: str) -> str:
        t0 = time.perf_counter()
        if self.latency_s:
            time.sleep(self.latency_s)
        completion = self._write(name, user)
        ms = (time.perf_counter() - t0) * 1000.0
        self.calls.append(CallLog(name, system, user, completion, ms))
        return completion

    def _write(self, name: str, user: str) -> str:
        if name == "extract":
            return (
                "service=payments-api; region=us-east-1; symptom=504s; "
                "duration=eleven minutes; cause=config push; "
                "checkout=delayed-not-lost; rollback=14:23; "
                "status_page=14:18; do_not_promise_eta=true"
            )
        if name in {"draft", "loop-draft"}:
            return (
                "We saw 504s on payments-api in us-east-1 for about eleven "
                "minutes after a config push. Checkout was delayed, not lost. "
                "We rolled the config back and posted to the status page. "
                "We are watching the service. We are not quoting a restore time."
            )
        if name in {"review", "loop-check"}:
            body = user
            if "DRAFT:" in user:
                after = user.split("DRAFT:", 1)[1]
                body = after.split("RUBRIC:", 1)[0] if "RUBRIC:" in after else after
            ok_name = "payments-api" in body
            ok_eta = not any(
                p in body.lower()
                for p in (
                    "by tomorrow",
                    "within the hour",
                    "eta:",
                    "will be up at",
                    "restore at",
                    "restore time is",
                )
            )
            promised = any(
                p in body.lower()
                for p in ("by tomorrow", "within the hour", "eta:", "will be up at")
            )
            n = words(body)
            ok_len = n < 80
            delayed = "delayed" in body.lower() and "lost" in body.lower()
            verdict = "PASS" if (ok_name and ok_eta and not promised and ok_len and delayed) else "FAIL"
            return (
                f"{verdict}; names_service={ok_name}; no_false_eta={not promised}; "
                f"under_80={ok_len}; delayed_not_lost={delayed}; words={n}"
            )
        raise ValueError(name)


LOOP_SYSTEM = (
    "You are a single status writer. Read the incident. Draft a customer "
    "paragraph. Then check the rubric in the same context. Do not invent "
    "an ETA. Keep the same voice across both turns."
)

EXTRACT_SYSTEM = (
    "You are the extract node. Pull fields from the incident. Do not draft. "
    "Do not talk to the customer. Return a field list."
)

DRAFT_SYSTEM = (
    "You are the draft node. You do not see the raw incident, only the "
    "extract node's field list. Write a customer paragraph. Do not review."
)

REVIEW_SYSTEM = (
    "You are the review node. You do not write. Score the draft against "
    "the rubric. Return PASS or FAIL and a flag list."
)


def run_loop(incident: str, rubric: str, *, latency_s: float = 0.02) -> Run:
    llm = MockLLM(latency_s=latency_s)
    t0 = time.perf_counter()
    draft = llm.complete(
        "loop-draft",
        LOOP_SYSTEM,
        f"INCIDENT:\n{incident}\n\nRUBRIC:\n{rubric}\n\nWrite the paragraph.",
    )
    check = llm.complete(
        "loop-check",
        LOOP_SYSTEM,
        f"INCIDENT:\n{incident}\n\nDRAFT:\n{draft}\n\nRUBRIC:\n{rubric}\n\nCheck the draft.",
    )
    wall = (time.perf_counter() - t0) * 1000.0
    return Run("loop", f"{draft}\n---\n{check}", llm.calls, wall, state_copies=0)


def run_graph(incident: str, rubric: str, *, latency_s: float = 0.02) -> Run:
    """Three sequential LLM-bearing nodes. No fan-out. State copied on each edge."""
    llm = MockLLM(latency_s=latency_s)
    t0 = time.perf_counter()
    copies = 0
    extract = llm.complete(
        "extract",
        EXTRACT_SYSTEM,
        f"INCIDENT:\n{incident}\n\nExtract fields.",
    )
    copies += words(extract)
    draft = llm.complete(
        "draft",
        DRAFT_SYSTEM,
        f"EXTRACT:\n{extract}\n\nRUBRIC:\n{rubric}\n\nWrite the paragraph.",
    )
    copies += words(draft)
    review = llm.complete(
        "review",
        REVIEW_SYSTEM,
        f"DRAFT:\n{draft}\n\nRUBRIC:\n{rubric}\n\nScore the draft.",
    )
    wall = (time.perf_counter() - t0) * 1000.0
    return Run(
        "three-node-graph",
        f"{extract}\n---\n{draft}\n---\n{review}",
        llm.calls,
        wall,
        state_copies=copies,
    )


def report(loop: Run, graph: Run) -> str:
    token_ratio = graph.tokens / loop.tokens if loop.tokens else float("inf")
    wall_ratio = graph.wall_ms / loop.wall_ms if loop.wall_ms else float("inf")
    lines = [
        "Ken/Lua loop-vs-graph bakeoff (sequential status paragraph; no fan-out)",
        f"loop: calls={loop.n_calls} tokens~{loop.tokens} wall_ms={loop.wall_ms:.1f} state_copies=0",
        (
            f"graph: calls={graph.n_calls} tokens~{graph.tokens} "
            f"wall_ms={graph.wall_ms:.1f} state_copies={graph.state_copies}"
        ),
        f"graph/loop token ratio: {token_ratio:.2f}x (estimates, this file only)",
        f"graph/loop wall-clock ratio: {wall_ratio:.2f}x (sequential; no parallelism to harvest)",
        "same deterministic writer in both arms; both arms emit the same paragraph because they share one deterministic writer; the file does not score quality",
        "per-call token estimates:",
    ]
    for arm in (loop, graph):
        for c in arm.calls:
            lines.append(
                f" {arm.arm:16s} {c.name:12s} sys={words(c.system):3d} "
                f"user={words(c.user):3d} out={words(c.completion):3d} tot={c.tokens}"
            )
    lines.append(
        "conclusion: extra sequential nodes added a call and ~1.5x wall-clock; "
        "they did not harvest parallelism because there was none; token estimates "
        "were within a few percent (loop resends the incident, graph compresses "
        "through extract and pays three system prompts). Same paragraph. Same PASS. "
        "The topology did not earn its keep."
    )
    return "\n".join(lines)


def main() -> None:
    loop = run_loop(INCIDENT, RUBRIC)
    graph = run_graph(INCIDENT, RUBRIC)
    print(report(loop, graph))
    print("--- loop output ---")
    print(loop.output)
    print("--- graph output ---")
    print(graph.output)


if __name__ == "__main__":
    main()

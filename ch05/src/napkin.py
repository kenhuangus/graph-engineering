"""Chapter 5 — napkin test: stay on a loop, or earn a graph.

A job that is one worker plus tools stays on a loop. A job whose fan-out
cardinality is unknown at design time must build a graph (dynamic Send).
Reasons come from a closed set; the function does not invent slogans.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Reason = Literal[
    "needs_fanout",
    "typed_handoff",
    "human_interrupt",
    "halt_contract",
    "unknown_cardinality",
]
REASONS: frozenset[str] = frozenset(
    {"needs_fanout", "typed_handoff", "human_interrupt", "halt_contract", "unknown_cardinality"}
)
Action = Literal["stay_on_loop", "build_graph"]


@dataclass(frozen=True)
class JobSpec:
    """Napkin-sized description of the work. Not a prompt."""

    workers: int
    tools: tuple[str, ...] = ()
    specialties: tuple[str, ...] = ()
    fanout: bool = False
    fanout_cardinality_known: bool | None = None  # None = n/a (no fanout)
    typed_handoffs: bool = False
    human_interrupt: bool = False
    halt_contract: bool = False  # needs an explicit halt node other than "the loop stops"


@dataclass(frozen=True)
class Decision:
    action: Action
    reasons: tuple[Reason, ...]


def napkin_test(job: JobSpec) -> Decision:
    """Return stay_on_loop or build_graph, with reasons from REASONS.

    `stay_on_loop` if and only if no graph-requiring reason fires.
    One worker plus tools, no fan-out, no interrupt, no typed handoff,
    no halt-contract: stay.
    """
    reasons: list[Reason] = []

    if job.fanout and job.fanout_cardinality_known is False:
        reasons.append("unknown_cardinality")
    if job.fanout and job.fanout_cardinality_known is not False:
        # known fan-out (or unspecified known) still needs a join topology
        reasons.append("needs_fanout")
    if job.fanout and job.fanout_cardinality_known is False:
        # unknown cardinality is the stronger statement; still also fan-out
        if "needs_fanout" not in reasons:
            reasons.append("needs_fanout")

    # Independent specialties that must hand typed state, not a chat blob.
    if job.typed_handoffs or (job.workers >= 2 and len(job.specialties) >= 2):
        reasons.append("typed_handoff")

    if job.human_interrupt:
        reasons.append("human_interrupt")

    if job.halt_contract:
        reasons.append("halt_contract")

    # Deduplicate while preserving order.
    seen: set[str] = set()
    ordered: list[Reason] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            ordered.append(r)

    if not ordered:
        return Decision(action="stay_on_loop", reasons=())
    return Decision(action="build_graph", reasons=tuple(ordered))
